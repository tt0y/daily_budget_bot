import unittest

from src.receipt_formatter import format_receipt_summary, receipt_expense_rows
from src.receipt_parser import ReceiptData, ReceiptItem


class TestMainFormatting(unittest.TestCase):

    def test_receipt_summary_mentions_receipt_date(self):
        receipt = ReceiptData(
            merchant="MERCADONA, S.A.",
            purchased_at="2026-06-14T13:21:34",
            currency="EUR",
            total=62.07,
            items=[
                ReceiptItem(name="Leche Entera P6", amount=5.76, category="groceries"),
                ReceiptItem(name="Higienico Doble Roll", amount=2.30, category="home"),
            ],
            notes=[],
        )

        text = format_receipt_summary(receipt, "ru")

        self.assertIn("Расходы записаны на дату чека: <b>2026-06-14</b>.", text)
        self.assertIn("✅ Чек сохранен: <b>MERCADONA, S.A.</b>", text)

    def test_receipt_summary_mentions_upload_date_fallback(self):
        receipt = ReceiptData(
            merchant=None,
            purchased_at=None,
            currency="EUR",
            total=10.0,
            items=[ReceiptItem(name="Something", amount=10.0, category="other")],
            notes=[],
        )

        text = format_receipt_summary(receipt, "ru")

        self.assertIn("Дату на чеке не распознал", text)

    def test_receipt_summary_adds_missing_total_to_other(self):
        receipt = ReceiptData(
            merchant="Mercadona S.A.",
            purchased_at="2023-02-13T12:00:00",
            currency="EUR",
            total=74.68,
            items=[
                ReceiptItem(name="Food", amount=59.81, category="groceries"),
                ReceiptItem(name="Home", amount=5.55, category="home"),
                ReceiptItem(name="Health", amount=2.00, category="health"),
                ReceiptItem(name="Other", amount=3.00, category="other"),
            ],
            notes=[],
        )

        text = format_receipt_summary(receipt, "ru")

        self.assertIn("• Другое: 7.32 (2)", text)
        self.assertIn("Разницу <b>4.32</b> добавил в <b>Другое</b>", text)
        self.assertNotIn("Проверь сумму", text)

    def test_receipt_expense_rows_include_missing_total_difference(self):
        receipt = ReceiptData(
            merchant="Mercadona S.A.",
            purchased_at="2023-02-13T12:00:00",
            currency="EUR",
            total=74.68,
            items=[
                ReceiptItem(name="Recognized", amount=70.36, category="groceries"),
            ],
            notes=[],
        )

        rows = receipt_expense_rows(receipt)

        self.assertEqual(rows[-1], {
            "amount": 4.32,
            "description": "Unrecognized receipt difference",
            "category": "other",
        })


if __name__ == '__main__':
    unittest.main()
