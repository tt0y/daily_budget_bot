import unittest

from src.receipt_formatter import format_receipt_summary
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


if __name__ == '__main__':
    unittest.main()
