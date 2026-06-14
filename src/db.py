
import aiosqlite
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

DB_NAME = os.getenv("DB_PATH", "finance_bot.db")



async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                income_day INTEGER NOT NULL,
                savings_percent REAL NOT NULL,
                language TEXT DEFAULT 'en',
                monthly_income REAL DEFAULT 0
            )
        ''')

        # Balance history: one row per reading (append-only), used to derive the
        # spending pace for the trend forecast. An earlier version keyed the table
        # by (user_id, snapshot_date), which collapsed several readings on the same
        # day into one row and starved the trend — migrate that schema away.
        async with db.execute("PRAGMA table_info(balance_history)") as cursor:
            bh_columns = [row[1] for row in await cursor.fetchall()]

        if not bh_columns:
            await db.execute('''
                CREATE TABLE balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    balance REAL NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            ''')
        elif 'snapshot_date' in bh_columns:
            await db.execute('ALTER TABLE balance_history RENAME TO balance_history_old')
            await db.execute('''
                CREATE TABLE balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    balance REAL NOT NULL,
                    recorded_at TEXT NOT NULL
                )
            ''')
            await db.execute('''
                INSERT INTO balance_history (user_id, balance, recorded_at)
                SELECT user_id, balance, recorded_at FROM balance_history_old
            ''')
            await db.execute('DROP TABLE balance_history_old')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                merchant TEXT,
                purchased_at TEXT,
                total REAL,
                currency TEXT DEFAULT 'EUR',
                source_type TEXT,
                created_at TEXT NOT NULL
            )
        ''')

        await db.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'other',
                date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')

        async with db.execute("PRAGMA table_info(expenses)") as cursor:
            expense_columns = [row[1] for row in await cursor.fetchall()]

        expense_migrations = {
            'receipt_id': 'ALTER TABLE expenses ADD COLUMN receipt_id INTEGER',
            'category': 'ALTER TABLE expenses ADD COLUMN category TEXT DEFAULT "other"',
            'date': 'ALTER TABLE expenses ADD COLUMN date TEXT',
            'created_at': 'ALTER TABLE expenses ADD COLUMN created_at TEXT',
        }
        for column, statement in expense_migrations.items():
            if column not in expense_columns:
                await db.execute(statement)

        now = datetime.now().isoformat(timespec='seconds')
        await db.execute('UPDATE expenses SET category = "other" WHERE category IS NULL OR category = ""')
        await db.execute('UPDATE expenses SET date = ? WHERE date IS NULL OR date = ""', (now,))
        await db.execute('UPDATE expenses SET created_at = date WHERE created_at IS NULL OR created_at = ""')

        # Attempt to add columns if they don't exist
        try:
            await db.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT "en"')
        except Exception:
            pass # Column likely exists
            
        try:
            await db.execute('ALTER TABLE users ADD COLUMN monthly_income REAL DEFAULT 0')
        except Exception:
            pass 
            
        await db.commit()

async def add_or_update_user(user_id: int, income_day: int, savings_percent: float, language: str = 'en', monthly_income: float = 0):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO users (user_id, income_day, savings_percent, language, monthly_income)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                income_day = excluded.income_day,
                savings_percent = excluded.savings_percent,
                language = excluded.language,
                monthly_income = excluded.monthly_income
        ''', (user_id, income_day, savings_percent, language, monthly_income))
        await db.commit()

async def update_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users SET language = ? WHERE user_id = ?
        ''', (language, user_id))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT income_day, savings_percent, language, monthly_income FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                lang = row[2] if row[2] else 'en'
                # Handle missing monthly_income (if it's somehow NULL or we didn't migrate properly but here defaulting to 0 is safe usually)
                monthly_income = row[3] if len(row) > 3 and row[3] is not None else 0
                return {
                    "income_day": row[0], 
                    "savings_percent": row[1], 
                    "language": lang,
                    "monthly_income": monthly_income
                }
            return None

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]

async def record_balance(user_id: int, balance: float, now: datetime = None):
    """Append a balance reading (one row per reading)."""
    if now is None:
        now = datetime.now()
    recorded_at = now.isoformat(timespec='seconds')
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO balance_history (user_id, balance, recorded_at)
            VALUES (?, ?, ?)
        ''', (user_id, balance, recorded_at))
        await db.commit()

async def get_balance_history(user_id: int):
    """Return [(timestamp: datetime, balance: float), ...] ordered oldest first."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT recorded_at, balance FROM balance_history
            WHERE user_id = ?
            ORDER BY recorded_at ASC, id ASC
        ''', (user_id,)) as cursor:
            rows = await cursor.fetchall()
            history = []
            for recorded_at, balance in rows:
                try:
                    ts = datetime.fromisoformat(recorded_at)
                except (TypeError, ValueError):
                    continue
                history.append((ts, balance))
            return history

async def add_receipt_expenses(
    user_id: int,
    merchant: str = None,
    purchased_at: str = None,
    total: float = None,
    currency: str = "EUR",
    items: list[dict] = None,
    source_type: str = "receipt",
):
    """Store a parsed receipt and its itemized expenses.

    `items` entries are dictionaries with `amount`, `description`, and
    `category`. Returns the created receipt id.
    """
    now = datetime.now().isoformat(timespec='seconds')
    expense_date = purchased_at or now
    items = items or []

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute('''
            INSERT INTO receipts (user_id, merchant, purchased_at, total, currency, source_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, merchant, purchased_at, total, currency, source_type, now))
        receipt_id = cursor.lastrowid

        for item in items:
            await db.execute('''
                INSERT INTO expenses (receipt_id, user_id, amount, description, category, date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                receipt_id,
                user_id,
                float(item["amount"]),
                item.get("description"),
                item.get("category") or "other",
                expense_date,
                now,
            ))

        await db.commit()
        return receipt_id

async def add_expense(user_id: int, amount: float, description: str = None, category: str = "other"):
    now = datetime.now().isoformat(timespec='seconds')
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO expenses (user_id, amount, description, category, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, amount, description, category, now, now))
        await db.commit()

async def get_today_expenses(user_id: int):
    today_str = datetime.now().strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT SUM(amount) FROM expenses
            WHERE user_id = ? AND date(date) = ?
        ''', (user_id, today_str)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row and row[0] else 0.0

async def get_today_expense_totals(user_id: int, now: datetime = None):
    if now is None:
        now = datetime.now()
    today_str = now.strftime('%Y-%m-%d')
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT category, SUM(amount), COUNT(*) FROM expenses
            WHERE user_id = ? AND date(date) = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
        ''', (user_id, today_str)) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "category": row[0] or "other",
                    "amount": row[1] or 0.0,
                    "count": row[2] or 0,
                }
                for row in rows
            ]

async def get_expense_totals(user_id: int, period: str = "added_today", now: datetime = None):
    if now is None:
        now = datetime.now()

    date_column = "created_at" if period == "added_today" else "date"
    params = [user_id]
    where = ["user_id = ?"]

    if period == "added_today":
        start_date = now.strftime('%Y-%m-%d')
        end_date = (now + relativedelta(days=1)).strftime('%Y-%m-%d')
        where.append(f"date({date_column}) >= ? AND date({date_column}) < ?")
        params.extend([start_date, end_date])
    elif period == "expense_month":
        month_start = now.replace(day=1).strftime('%Y-%m-%d')
        next_month = (now.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d')
        where.append(f"date({date_column}) >= ? AND date({date_column}) < ?")
        params.extend([month_start, next_month])
    elif period == "all":
        pass
    else:
        raise ValueError(f"Unsupported stats period: {period}")

    query = f'''
        SELECT category, SUM(amount), COUNT(*) FROM expenses
        WHERE {' AND '.join(where)}
        GROUP BY category
        ORDER BY SUM(amount) DESC
    '''

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "category": row[0] or "other",
                    "amount": row[1] or 0.0,
                    "count": row[2] or 0,
                }
                for row in rows
            ]
