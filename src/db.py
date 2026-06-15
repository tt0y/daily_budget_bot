import os
import secrets
import string
from datetime import datetime

import aiosqlite
from dateutil.relativedelta import relativedelta

DB_NAME = os.getenv("DB_PATH", "finance_bot.db")

INVITE_ALPHABET = string.ascii_uppercase + "23456789"


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _normalize_invite_code(invite_code: str) -> str:
    return (invite_code or "").strip().upper()


async def _table_columns(db, table_name: str) -> list[str]:
    async with db.execute(f"PRAGMA table_info({table_name})") as cursor:
        return [row[1] for row in await cursor.fetchall()]


async def _ensure_column(db, table_name: str, columns: list[str], column_name: str, definition: str) -> None:
    if column_name not in columns:
        await db.execute(f"ALTER TABLE {table_name} ADD COLUMN {definition}")
        columns.append(column_name)


async def _generate_invite_code(db) -> str:
    while True:
        code = "".join(secrets.choice(INVITE_ALPHABET) for _ in range(8))
        async with db.execute("SELECT 1 FROM households WHERE invite_code = ?", (code,)) as cursor:
            if not await cursor.fetchone():
                return code


async def _create_household(
    db,
    user_id: int,
    income_day: int,
    savings_percent: float,
    monthly_income: float = 0,
    name: str | None = None,
) -> int:
    now = _now_iso()
    invite_code = await _generate_invite_code(db)
    household_name = name or "Personal budget"
    cursor = await db.execute(
        """
        INSERT INTO households (
            name,
            income_day,
            savings_percent,
            monthly_income,
            created_by_user_id,
            invite_code,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            household_name,
            income_day,
            savings_percent,
            monthly_income,
            user_id,
            invite_code,
            now,
        ),
    )
    household_id = cursor.lastrowid
    await db.execute(
        """
        INSERT OR IGNORE INTO household_members (household_id, user_id, role, joined_at)
        VALUES (?, ?, ?, ?)
        """,
        (household_id, user_id, "owner", now),
    )
    return household_id


async def _household_exists(db, household_id: int | None) -> bool:
    if household_id is None:
        return False
    async with db.execute("SELECT 1 FROM households WHERE id = ?", (household_id,)) as cursor:
        return await cursor.fetchone() is not None


async def _resolve_active_household_id(
    db,
    user_id: int,
    language: str = "en",
    default_income_day: int = 1,
    default_savings_percent: float = 0,
    default_monthly_income: float = 0,
) -> int:
    async with db.execute(
        """
        SELECT income_day, savings_percent, language, monthly_income, active_household_id
        FROM users
        WHERE user_id = ?
        """,
        (user_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        await db.execute(
            """
            INSERT INTO users (user_id, income_day, savings_percent, language, monthly_income)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, default_income_day, default_savings_percent, language, default_monthly_income),
        )
        household_id = await _create_household(
            db,
            user_id,
            default_income_day,
            default_savings_percent,
            default_monthly_income,
        )
        await db.execute(
            "UPDATE users SET active_household_id = ? WHERE user_id = ?",
            (household_id, user_id),
        )
        return household_id

    income_day = row[0] or default_income_day
    savings_percent = row[1] if row[1] is not None else default_savings_percent
    monthly_income = row[3] if row[3] is not None else default_monthly_income
    active_household_id = row[4]

    if await _household_exists(db, active_household_id):
        await db.execute(
            """
            INSERT OR IGNORE INTO household_members (household_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
            """,
            (active_household_id, user_id, "member", _now_iso()),
        )
        return active_household_id

    household_id = await _create_household(
        db,
        user_id,
        income_day,
        savings_percent,
        monthly_income,
    )
    await db.execute(
        "UPDATE users SET active_household_id = ? WHERE user_id = ?",
        (household_id, user_id),
    )
    return household_id


async def _ensure_invite_codes(db) -> None:
    async with db.execute(
        "SELECT id FROM households WHERE invite_code IS NULL OR invite_code = ''"
    ) as cursor:
        rows = await cursor.fetchall()

    for row in rows:
        invite_code = await _generate_invite_code(db)
        await db.execute(
            "UPDATE households SET invite_code = ? WHERE id = ?",
            (invite_code, row[0]),
        )


async def _backfill_personal_households(db) -> None:
    async with db.execute(
        """
        SELECT user_id, income_day, savings_percent, monthly_income, active_household_id
        FROM users
        """
    ) as cursor:
        users = await cursor.fetchall()

    for user_id, income_day, savings_percent, monthly_income, active_household_id in users:
        if await _household_exists(db, active_household_id):
            await db.execute(
                """
                INSERT OR IGNORE INTO household_members (household_id, user_id, role, joined_at)
                VALUES (?, ?, ?, ?)
                """,
                (active_household_id, user_id, "owner", _now_iso()),
            )
            continue

        household_id = await _create_household(
            db,
            user_id,
            income_day or 1,
            savings_percent if savings_percent is not None else 0,
            monthly_income if monthly_income is not None else 0,
        )
        await db.execute(
            "UPDATE users SET active_household_id = ? WHERE user_id = ?",
            (household_id, user_id),
        )


async def _backfill_household_id(db, table_name: str) -> None:
    await db.execute(
        f"""
        UPDATE {table_name}
        SET household_id = (
            SELECT active_household_id FROM users WHERE users.user_id = {table_name}.user_id
        )
        WHERE household_id IS NULL
        """
    )


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                income_day INTEGER NOT NULL,
                savings_percent REAL NOT NULL,
                language TEXT DEFAULT 'en',
                monthly_income REAL DEFAULT 0,
                active_household_id INTEGER
            )
            """
        )

        user_columns = await _table_columns(db, "users")
        await _ensure_column(db, "users", user_columns, "language", 'language TEXT DEFAULT "en"')
        await _ensure_column(db, "users", user_columns, "monthly_income", "monthly_income REAL DEFAULT 0")
        await _ensure_column(db, "users", user_columns, "active_household_id", "active_household_id INTEGER")

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS households (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                income_day INTEGER NOT NULL,
                savings_percent REAL NOT NULL,
                monthly_income REAL DEFAULT 0,
                created_by_user_id INTEGER NOT NULL,
                invite_code TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        household_columns = await _table_columns(db, "households")
        await _ensure_column(db, "households", household_columns, "invite_code", "invite_code TEXT")
        await _ensure_column(db, "households", household_columns, "created_at", "created_at TEXT")
        await _ensure_invite_codes(db)
        await db.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_households_invite_code ON households(invite_code)"
        )

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS household_members (
                household_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                role TEXT NOT NULL DEFAULT 'member',
                joined_at TEXT NOT NULL,
                PRIMARY KEY (household_id, user_id)
            )
            """
        )

        await _backfill_personal_households(db)

        # Balance history: one row per reading (append-only), used to derive the
        # spending pace for the trend forecast. An earlier version keyed the table
        # by (user_id, snapshot_date), which collapsed several readings on the same
        # day into one row and starved the trend. Migrate that schema away.
        bh_columns = await _table_columns(db, "balance_history")

        if not bh_columns:
            await db.execute(
                """
                CREATE TABLE balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    household_id INTEGER,
                    user_id INTEGER NOT NULL,
                    balance REAL NOT NULL,
                    recorded_at TEXT NOT NULL
                )
                """
            )
        elif "snapshot_date" in bh_columns:
            await db.execute("ALTER TABLE balance_history RENAME TO balance_history_old")
            await db.execute(
                """
                CREATE TABLE balance_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    household_id INTEGER,
                    user_id INTEGER NOT NULL,
                    balance REAL NOT NULL,
                    recorded_at TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                INSERT INTO balance_history (user_id, balance, recorded_at)
                SELECT user_id, balance, recorded_at FROM balance_history_old
                """
            )
            await db.execute("DROP TABLE balance_history_old")
        else:
            await _ensure_column(db, "balance_history", bh_columns, "household_id", "household_id INTEGER")

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                household_id INTEGER,
                user_id INTEGER NOT NULL,
                merchant TEXT,
                purchased_at TEXT,
                total REAL,
                currency TEXT DEFAULT 'EUR',
                source_type TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        receipt_columns = await _table_columns(db, "receipts")
        await _ensure_column(db, "receipts", receipt_columns, "household_id", "household_id INTEGER")

        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                household_id INTEGER,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'other',
                date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        expense_columns = await _table_columns(db, "expenses")
        expense_migrations = {
            "receipt_id": "receipt_id INTEGER",
            "household_id": "household_id INTEGER",
            "category": 'category TEXT DEFAULT "other"',
            "date": "date TEXT",
            "created_at": "created_at TEXT",
        }
        for column, definition in expense_migrations.items():
            await _ensure_column(db, "expenses", expense_columns, column, definition)

        now = _now_iso()
        await db.execute('UPDATE expenses SET category = "other" WHERE category IS NULL OR category = ""')
        await db.execute('UPDATE expenses SET date = ? WHERE date IS NULL OR date = ""', (now,))
        await db.execute('UPDATE expenses SET created_at = date WHERE created_at IS NULL OR created_at = ""')

        await _backfill_household_id(db, "balance_history")
        await _backfill_household_id(db, "receipts")
        await _backfill_household_id(db, "expenses")

        await db.commit()


async def add_or_update_user(
    user_id: int,
    income_day: int,
    savings_percent: float,
    language: str = "en",
    monthly_income: float = 0,
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, income_day, savings_percent, language, monthly_income)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                income_day = excluded.income_day,
                savings_percent = excluded.savings_percent,
                language = excluded.language,
                monthly_income = excluded.monthly_income
            """,
            (user_id, income_day, savings_percent, language, monthly_income),
        )
        household_id = await _resolve_active_household_id(
            db,
            user_id,
            language=language,
            default_income_day=income_day,
            default_savings_percent=savings_percent,
            default_monthly_income=monthly_income,
        )
        await db.execute(
            """
            UPDATE households
            SET income_day = ?, savings_percent = ?, monthly_income = ?
            WHERE id = ?
            """,
            (income_day, savings_percent, monthly_income, household_id),
        )
        await db.commit()


async def update_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users SET language = ? WHERE user_id = ?
            """,
            (language, user_id),
        )
        await db.commit()


async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT
                u.income_day,
                u.savings_percent,
                u.language,
                u.monthly_income,
                u.active_household_id,
                h.name,
                h.income_day,
                h.savings_percent,
                h.monthly_income
            FROM users u
            LEFT JOIN households h ON h.id = u.active_household_id
            WHERE u.user_id = ?
            """,
            (user_id,),
        ) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        lang = row[2] if row[2] else "en"
        household_id = row[4]
        household_name = row[5] or "Personal budget"
        income_day = row[6] if row[6] is not None else row[0]
        savings_percent = row[7] if row[7] is not None else row[1]
        monthly_income = row[8] if row[8] is not None else row[3]

        return {
            "income_day": income_day,
            "savings_percent": savings_percent,
            "language": lang,
            "monthly_income": monthly_income if monthly_income is not None else 0,
            "household_id": household_id,
            "household_name": household_name,
        }


async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT user_id FROM users") as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]


async def get_active_household(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        household_id = await _resolve_active_household_id(db, user_id)
        async with db.execute(
            """
            SELECT id, name, income_day, savings_percent, monthly_income, invite_code
            FROM households
            WHERE id = ?
            """,
            (household_id,),
        ) as cursor:
            row = await cursor.fetchone()
        await db.commit()

    if not row:
        return None

    return {
        "id": row[0],
        "name": row[1],
        "income_day": row[2],
        "savings_percent": row[3],
        "monthly_income": row[4] if row[4] is not None else 0,
        "invite_code": row[5],
    }


async def get_household_members(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        household_id = await _resolve_active_household_id(db, user_id)
        async with db.execute(
            """
            SELECT user_id, role, joined_at
            FROM household_members
            WHERE household_id = ?
            ORDER BY role = 'owner' DESC, joined_at ASC, user_id ASC
            """,
            (household_id,),
        ) as cursor:
            rows = await cursor.fetchall()
        await db.commit()

    return [
        {
            "user_id": row[0],
            "role": row[1],
            "joined_at": row[2],
        }
        for row in rows
    ]


async def get_or_create_household_invite_code(user_id: int) -> str:
    async with aiosqlite.connect(DB_NAME) as db:
        household_id = await _resolve_active_household_id(db, user_id)
        async with db.execute(
            "SELECT invite_code FROM households WHERE id = ?",
            (household_id,),
        ) as cursor:
            row = await cursor.fetchone()

        invite_code = row[0] if row else None
        if not invite_code:
            invite_code = await _generate_invite_code(db)
            await db.execute(
                "UPDATE households SET invite_code = ? WHERE id = ?",
                (invite_code, household_id),
            )

        await db.commit()
        return invite_code


async def join_household_by_invite(user_id: int, invite_code: str, language: str = "en"):
    normalized_code = _normalize_invite_code(invite_code)
    if not normalized_code:
        return None

    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute(
            """
            SELECT id, name, income_day, savings_percent, monthly_income
            FROM households
            WHERE UPPER(invite_code) = ?
            """,
            (normalized_code,),
        ) as cursor:
            household = await cursor.fetchone()

        if not household:
            return None

        household_id, name, income_day, savings_percent, monthly_income = household
        now = _now_iso()
        await db.execute(
            """
            INSERT INTO users (
                user_id,
                income_day,
                savings_percent,
                language,
                monthly_income,
                active_household_id
            )
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                income_day = excluded.income_day,
                savings_percent = excluded.savings_percent,
                monthly_income = excluded.monthly_income,
                active_household_id = excluded.active_household_id
            """,
            (
                user_id,
                income_day,
                savings_percent,
                language,
                monthly_income if monthly_income is not None else 0,
                household_id,
            ),
        )
        await db.execute(
            """
            INSERT OR IGNORE INTO household_members (household_id, user_id, role, joined_at)
            VALUES (?, ?, ?, ?)
            """,
            (household_id, user_id, "member", now),
        )
        await db.commit()

    return {
        "id": household_id,
        "name": name,
        "income_day": income_day,
        "savings_percent": savings_percent,
        "monthly_income": monthly_income if monthly_income is not None else 0,
    }


async def record_balance(user_id: int, balance: float, now: datetime = None, household_id: int | None = None):
    """Append a balance reading for the user's active household."""
    if now is None:
        now = datetime.now()
    recorded_at = now.isoformat(timespec="seconds")
    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)
        await db.execute(
            """
            INSERT INTO balance_history (household_id, user_id, balance, recorded_at)
            VALUES (?, ?, ?, ?)
            """,
            (household_id, user_id, balance, recorded_at),
        )
        await db.commit()


async def get_balance_history(user_id: int, household_id: int | None = None):
    """Return [(timestamp: datetime, balance: float), ...] ordered oldest first."""
    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)
        async with db.execute(
            """
            SELECT recorded_at, balance FROM balance_history
            WHERE household_id = ?
            ORDER BY recorded_at ASC, id ASC
            """,
            (household_id,),
        ) as cursor:
            rows = await cursor.fetchall()
        await db.commit()

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
    household_id: int | None = None,
):
    """Store a parsed receipt and its itemized expenses.

    `items` entries are dictionaries with `amount`, `description`, and
    `category`. Returns the created receipt id.
    """
    now = _now_iso()
    expense_date = purchased_at or now
    items = items or []

    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)
        cursor = await db.execute(
            """
            INSERT INTO receipts (
                household_id,
                user_id,
                merchant,
                purchased_at,
                total,
                currency,
                source_type,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (household_id, user_id, merchant, purchased_at, total, currency, source_type, now),
        )
        receipt_id = cursor.lastrowid

        for item in items:
            await db.execute(
                """
                INSERT INTO expenses (
                    receipt_id,
                    household_id,
                    user_id,
                    amount,
                    description,
                    category,
                    date,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    receipt_id,
                    household_id,
                    user_id,
                    float(item["amount"]),
                    item.get("description"),
                    item.get("category") or "other",
                    expense_date,
                    now,
                ),
            )

        await db.commit()
        return receipt_id


async def add_expense(
    user_id: int,
    amount: float,
    description: str = None,
    category: str = "other",
    household_id: int | None = None,
):
    now = _now_iso()
    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)
        await db.execute(
            """
            INSERT INTO expenses (household_id, user_id, amount, description, category, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (household_id, user_id, amount, description, category, now, now),
        )
        await db.commit()


async def get_today_expenses(user_id: int, household_id: int | None = None):
    today_str = datetime.now().strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)
        async with db.execute(
            """
            SELECT SUM(amount) FROM expenses
            WHERE household_id = ? AND date(date) = ?
            """,
            (household_id, today_str),
        ) as cursor:
            row = await cursor.fetchone()
        await db.commit()
        return row[0] if row and row[0] else 0.0


async def get_today_expense_totals(user_id: int, now: datetime = None, household_id: int | None = None):
    if now is None:
        now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)
        async with db.execute(
            """
            SELECT category, SUM(amount), COUNT(*) FROM expenses
            WHERE household_id = ? AND date(date) = ?
            GROUP BY category
            ORDER BY SUM(amount) DESC
            """,
            (household_id, today_str),
        ) as cursor:
            rows = await cursor.fetchall()
        await db.commit()

    return [
        {
            "category": row[0] or "other",
            "amount": row[1] or 0.0,
            "count": row[2] or 0,
        }
        for row in rows
    ]


async def get_expense_totals(
    user_id: int,
    period: str = "added_today",
    now: datetime = None,
    household_id: int | None = None,
):
    if now is None:
        now = datetime.now()

    date_column = "created_at" if period == "added_today" else "date"

    async with aiosqlite.connect(DB_NAME) as db:
        if household_id is None:
            household_id = await _resolve_active_household_id(db, user_id)

        params = [household_id]
        where = ["household_id = ?"]

        if period == "added_today":
            start_date = now.strftime("%Y-%m-%d")
            end_date = (now + relativedelta(days=1)).strftime("%Y-%m-%d")
            where.append(f"date({date_column}) >= ? AND date({date_column}) < ?")
            params.extend([start_date, end_date])
        elif period == "expense_month":
            month_start = now.replace(day=1).strftime("%Y-%m-%d")
            next_month = (now.replace(day=1) + relativedelta(months=1)).strftime("%Y-%m-%d")
            where.append(f"date({date_column}) >= ? AND date({date_column}) < ?")
            params.extend([month_start, next_month])
        elif period == "expense_year":
            year_start = now.replace(month=1, day=1).strftime("%Y-%m-%d")
            next_year = (now.replace(month=1, day=1) + relativedelta(years=1)).strftime("%Y-%m-%d")
            where.append(f"date({date_column}) >= ? AND date({date_column}) < ?")
            params.extend([year_start, next_year])
        elif period == "all":
            pass
        else:
            raise ValueError(f"Unsupported stats period: {period}")

        query = f"""
            SELECT category, SUM(amount), COUNT(*) FROM expenses
            WHERE {' AND '.join(where)}
            GROUP BY category
            ORDER BY SUM(amount) DESC
        """

        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
        await db.commit()

    return [
        {
            "category": row[0] or "other",
            "amount": row[1] or 0.0,
            "count": row[2] or 0,
        }
        for row in rows
    ]
