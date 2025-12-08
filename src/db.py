
import aiosqlite
import os

DB_NAME = os.getenv("DB_PATH", "finance_bot.db")

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                income_day INTEGER NOT NULL,
                savings_percent REAL NOT NULL
            )
        ''')
        await db.commit()

async def add_or_update_user(user_id: int, income_day: int, savings_percent: float):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT INTO users (user_id, income_day, savings_percent)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                income_day = excluded.income_day,
                savings_percent = excluded.savings_percent
        ''', (user_id, income_day, savings_percent))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT income_day, savings_percent FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"income_day": row[0], "savings_percent": row[1]}
            return None
