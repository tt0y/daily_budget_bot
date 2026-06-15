import os
import sqlite3
import tempfile
import unittest
from datetime import datetime

from src import db as db_module


class TestFamilyBudgetDatabase(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.previous_db_name = db_module.DB_NAME
        db_module.DB_NAME = self.tmp.name
        await db_module.init_db()

    async def asyncTearDown(self):
        db_module.DB_NAME = self.previous_db_name
        os.unlink(self.tmp.name)

    async def test_invited_member_shares_expenses_stats_and_balance_history(self):
        await db_module.add_or_update_user(
            user_id=1001,
            income_day=25,
            savings_percent=10,
            language="en",
            monthly_income=3000,
        )
        owner = await db_module.get_user(1001)
        invite_code = await db_module.get_or_create_household_invite_code(1001)

        household = await db_module.join_household_by_invite(
            user_id=2002,
            invite_code=invite_code.lower(),
            language="ru",
        )
        member = await db_module.get_user(2002)

        self.assertIsNotNone(household)
        self.assertEqual(household["id"], owner["household_id"])
        self.assertEqual(member["household_id"], owner["household_id"])
        self.assertEqual(member["language"], "ru")
        self.assertEqual(member["income_day"], 25)
        self.assertEqual(member["monthly_income"], 3000)

        await db_module.add_expense(1001, 10, "Bread", "groceries")
        await db_module.add_expense(2002, 5, "Soap", "home")
        await db_module.add_income(1001, 3000, "Salary")
        await db_module.add_income(2002, 500, "Bonus")

        owner_totals = await db_module.get_expense_totals(1001, period="all")
        member_totals = await db_module.get_expense_totals(2002, period="all")
        totals_by_category = {row["category"]: row["amount"] for row in owner_totals}
        owner_income_totals = await db_module.get_income_totals(1001, period="all")
        member_income_totals = await db_module.get_income_totals(2002, period="all")
        income_by_description = {row["description"]: row["amount"] for row in owner_income_totals}

        self.assertEqual(owner_totals, member_totals)
        self.assertEqual(totals_by_category, {"groceries": 10, "home": 5})
        self.assertEqual(owner_income_totals, member_income_totals)
        self.assertEqual(income_by_description, {"Salary": 3000, "Bonus": 500})

        await db_module.record_balance(1001, 1000, datetime(2026, 6, 15, 10, 0, 0))
        await db_module.record_balance(2002, 900, datetime(2026, 6, 16, 10, 0, 0))

        owner_history = await db_module.get_balance_history(1001)
        member_history = await db_module.get_balance_history(2002)

        self.assertEqual(owner_history, member_history)
        self.assertEqual([balance for _, balance in owner_history], [1000, 900])

    async def test_joining_family_keeps_previous_personal_expenses_separate(self):
        await db_module.add_expense(2002, 99, "Private expense", "other")
        personal_totals = await db_module.get_expense_totals(2002, period="all")
        self.assertEqual(personal_totals[0]["amount"], 99)

        await db_module.add_or_update_user(
            user_id=1001,
            income_day=25,
            savings_percent=10,
            language="en",
            monthly_income=3000,
        )
        invite_code = await db_module.get_or_create_household_invite_code(1001)
        await db_module.join_household_by_invite(2002, invite_code, language="ru")

        family_totals = await db_module.get_expense_totals(2002, period="all")
        self.assertEqual(family_totals, [])


class TestFamilyBudgetMigration(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.previous_db_name = db_module.DB_NAME
        db_module.DB_NAME = self.tmp.name

    async def asyncTearDown(self):
        db_module.DB_NAME = self.previous_db_name
        os.unlink(self.tmp.name)

    async def test_existing_single_user_data_gets_personal_household(self):
        conn = sqlite3.connect(self.tmp.name)
        conn.execute(
            """
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY,
                income_day INTEGER NOT NULL,
                savings_percent REAL NOT NULL,
                language TEXT DEFAULT 'en',
                monthly_income REAL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'other',
                date TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        conn.execute(
            """
            CREATE TABLE balance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                balance REAL NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )
        conn.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (42, 15, 20, "ru", 2500))
        conn.execute(
            """
            INSERT INTO expenses (user_id, amount, description, category, date, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (42, 12.5, "Old expense", "groceries", "2026-06-15T12:00:00", "2026-06-15T12:00:00"),
        )
        conn.execute(
            """
            INSERT INTO receipts (user_id, merchant, purchased_at, total, currency, source_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (42, "Old shop", "2026-06-15T12:00:00", 12.5, "EUR", "receipt", "2026-06-15T12:01:00"),
        )
        conn.execute(
            """
            INSERT INTO balance_history (user_id, balance, recorded_at)
            VALUES (?, ?, ?)
            """,
            (42, 1000, "2026-06-15T10:00:00"),
        )
        conn.commit()
        conn.close()

        await db_module.init_db()

        user = await db_module.get_user(42)
        totals = await db_module.get_expense_totals(42, period="all")
        history = await db_module.get_balance_history(42)
        await db_module.add_income(42, 500, "Migrated income")
        income_totals = await db_module.get_income_totals(42, period="all")

        self.assertIsNotNone(user["household_id"])
        self.assertEqual(user["language"], "ru")
        self.assertEqual(user["income_day"], 15)
        self.assertEqual(totals[0]["amount"], 12.5)
        self.assertEqual([balance for _, balance in history], [1000])
        self.assertEqual(income_totals[0]["amount"], 500)


if __name__ == "__main__":
    unittest.main()
