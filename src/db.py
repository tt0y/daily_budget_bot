
import aiosqlite
import os
from datetime import datetime

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

        # One balance reading per user per day (latest wins). Used to derive the
        # actual spending pace for the budget trend forecast.
        await db.execute('''
            CREATE TABLE IF NOT EXISTS balance_history (
                user_id INTEGER NOT NULL,
                snapshot_date TEXT NOT NULL,
                balance REAL NOT NULL,
                recorded_at TEXT NOT NULL,
                PRIMARY KEY (user_id, snapshot_date)
            )
        ''')

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
    """Store today's balance reading (one row per user per day, latest wins)."""
    if now is None:
        now = datetime.now()
    snapshot_date = now.strftime('%Y-%m-%d')
    recorded_at = now.isoformat(timespec='seconds')
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO balance_history (user_id, snapshot_date, balance, recorded_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, snapshot_date) DO UPDATE SET
                balance = excluded.balance,
                recorded_at = excluded.recorded_at
        ''', (user_id, snapshot_date, balance, recorded_at))
        await db.commit()

async def get_balance_history(user_id: int):
    """Return [(timestamp: datetime, balance: float), ...] ordered oldest first."""
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('''
            SELECT recorded_at, balance FROM balance_history
            WHERE user_id = ?
            ORDER BY recorded_at ASC
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
