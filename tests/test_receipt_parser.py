import os
import tempfile
import unittest
from datetime import datetime

from src import db as db_module
from src.receipt_parser import (
    category_label,
    is_supported_receipt_file,
    parse_money,
    parse_receipt_response,
    summarize_categories,
)


class TestReceiptParser(unittest.TestCase):

    def test_parse_money_accepts_spanish_decimal_format(self):
        self.assertEqual(parse_money("8,99 €"), 8.99)
        self.assertEqual(parse_money("1.234,56"), 1234.56)
        self.assertEqual(parse_money("$9.70"), 9.70)

    def test_supported_receipt_file_accepts_image_extension_without_mime(self):
        self.assertTrue(is_supported_receipt_file("application/octet-stream", "receipt.jpg"))
        self.assertTrue(is_supported_receipt_file("application/pdf", None))
        self.assertFalse(is_supported_receipt_file("text/plain", "notes.txt"))

    def test_parse_receipt_response_normalizes_items_and_categories(self):
        receipt = parse_receipt_response("""
        ```json
        {
          "merchant": "Mercadona",
          "currency": "eur",
          "purchased_at": "27/04/2026 09:23",
          "total": "25,34",
          "items": [
            {"name": "24 HUEVOS FRESCOS", "quantity": 1, "amount": "5,60", "category": "Продукты", "confidence": 0.95},
            {"name": "PAPEL HIGIENICO", "quantity": 1, "amount": "3,55", "category": "household", "confidence": 0.86},
            {"name": "TOTAL", "amount": 0, "category": "other"}
          ],
          "notes": []
        }
        ```
        """)

        self.assertEqual(receipt.merchant, "Mercadona")
        self.assertEqual(receipt.purchased_at, "2026-04-27T09:23:00")
        self.assertEqual(receipt.currency, "EUR")
        self.assertEqual(receipt.total, 25.34)
        self.assertEqual(len(receipt.items), 2)
        self.assertEqual(receipt.items[0].category, "groceries")
        self.assertEqual(receipt.items[1].category, "home")

    def test_summarize_categories_orders_by_total(self):
        receipt = parse_receipt_response({
            "items": [
                {"name": "Bread", "amount": 1.5, "category": "groceries"},
                {"name": "Soap", "amount": 4.0, "category": "home"},
                {"name": "Cheese", "amount": 3.0, "category": "groceries"},
            ]
        })

        summary = summarize_categories(receipt.items)

        self.assertEqual(summary[0], ("groceries", 4.5, 2))
        self.assertEqual(summary[1], ("home", 4.0, 1))
        self.assertEqual(category_label("groceries", "ru"), "Продукты")


class TestReceiptDatabase(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        self.tmp.close()
        self.previous_db_name = db_module.DB_NAME
        db_module.DB_NAME = self.tmp.name
        await db_module.init_db()

    async def asyncTearDown(self):
        db_module.DB_NAME = self.previous_db_name
        os.unlink(self.tmp.name)

    async def test_add_receipt_expenses_and_today_totals(self):
        receipt_id = await db_module.add_receipt_expenses(
            user_id=42,
            merchant="Consum",
            purchased_at="2026-06-14T12:00:00",
            total=8.99,
            currency="EUR",
            items=[
                {"description": "AGUA", "amount": 3.95, "category": "groceries"},
                {"description": "PAPEL", "amount": 2.00, "category": "home"},
                {"description": "CERVEZA", "amount": 3.04, "category": "groceries"},
            ],
        )

        totals = await db_module.get_today_expense_totals(user_id=42, now=datetime(2026, 6, 14))

        self.assertEqual(receipt_id, 1)
        self.assertEqual(totals[0]["category"], "groceries")
        self.assertAlmostEqual(totals[0]["amount"], 6.99)
        self.assertEqual(totals[0]["count"], 2)
        self.assertEqual(totals[1]["category"], "home")


if __name__ == '__main__':
    unittest.main()
