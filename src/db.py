
import aiosqlite
import os

DB_NAME = os.getenv("DB_PATH", "finance_bot.db")


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                income_day INTEGER NOT NULL,
                savings_percent REAL NOT NULL,
                language TEXT DEFAULT 'en'
            )
        ''')
        # Attempt to add column if it doesn't exist (migration for existing db)
        try:
            await db.execute('ALTER TABLE users ADD COLUMN language TEXT DEFAULT "en"')
        except Exception:
            pass # Column likely exists
            
        await db.commit()

async def add_or_update_user(user_id: int, income_day: int, savings_percent: float, language: str = 'en'):
    async with aiosqlite.connect(DB_NAME) as db:
        # Check if user exists to preserve language if not provided or just update everything
        # Actually easier to just update logic. 
        # But wait, if we are in settings flow, we might not want to overwrite language if we don't pass it?
        # The current flow updates income_day and savings_percent together.
        # Let's keep language decoupled or allow it to be passed.
        # If we use ON CONFLICT DO UPDATE, we need to be careful.
        
        # Current usage in main.py passes 3 args.
        # To make it backward compatible or easy, we can fetch existing language if needed?
        # Or just default to 'en' is risky if we overwrite.
        # BUT, the settings flow currently recalculates everything.
        # Let's see how main.py calls it. It calls it after getting income_day and savings_percent.
        
        # Better approach: update specific fields?
        # For now let's change signature to allow updating all.
        # If we want to only update language, we might need a separate function.
        
        await db.execute('''
            INSERT INTO users (user_id, income_day, savings_percent, language)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                income_day = excluded.income_day,
                savings_percent = excluded.savings_percent,
                language = excluded.language
        ''', (user_id, income_day, savings_percent, language))
        await db.commit()

async def update_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            UPDATE users SET language = ? WHERE user_id = ?
        ''', (language, user_id))
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT income_day, savings_percent, language FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                # Handle case where language is NULL (if that happened)
                lang = row[2] if row[2] else 'en'
                return {"income_day": row[0], "savings_percent": row[1], "language": lang}
            return None

async def get_all_users():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT user_id FROM users') as cursor:
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
