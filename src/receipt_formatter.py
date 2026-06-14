from datetime import datetime
from html import escape

try:
    from messages import get_text
    from receipt_parser import ReceiptData, ReceiptItem, category_label, summarize_categories
except ImportError:
    from .messages import get_text
    from .receipt_parser import ReceiptData, ReceiptItem, category_label, summarize_categories


def format_receipt_summary(receipt: ReceiptData, lang: str) -> str:
    merchant = escape(receipt.merchant or get_text("receipt_unknown_store", lang))
    total_value = receipt.total if receipt.total is not None else receipt.items_total
    items_with_adjustment = receipt_items_with_adjustment(receipt)
    receipt_date = format_receipt_expense_date(receipt.purchased_at)
    date_line_key = "receipt_date_saved" if receipt_date else "receipt_date_fallback"
    lines = [
        get_text(date_line_key, lang, date=receipt_date),
        "",
        get_text(
            "receipt_saved",
            lang,
            merchant=merchant,
            total=f"{total_value:.2f}",
            currency=escape(receipt.currency),
            count=len(items_with_adjustment),
        ),
        "",
        get_text("receipt_categories_header", lang),
    ]

    for category_id, amount, count in summarize_categories(items_with_adjustment):
        lines.append(f"• {escape(category_label(category_id, lang))}: {amount:.2f} ({count})")

    shown_items = items_with_adjustment[:8]
    if shown_items:
        lines.append("")
        lines.append(get_text("receipt_items_header", lang))
        for item in shown_items:
            lines.append(
                f"• {escape(item.name)} - {item.amount:.2f} "
                f"-> {escape(category_label(item.category, lang))}"
            )

    hidden_count = len(items_with_adjustment) - len(shown_items)
    if hidden_count > 0:
        lines.append(get_text("receipt_more_items", lang, count=hidden_count))

    missing_amount = get_receipt_missing_amount(receipt)
    if missing_amount:
        lines.append("")
        lines.append(get_text(
            "receipt_total_adjusted",
            lang,
            amount=f"{missing_amount:.2f}",
        ))
    elif receipt.total is not None and receipt.items_total - receipt.total > 0.05:
        lines.append("")
        lines.append(get_text(
            "receipt_total_mismatch",
            lang,
            items_total=f"{receipt.items_total:.2f}",
            receipt_total=f"{receipt.total:.2f}",
        ))

    return "\n".join(lines)


def receipt_items_with_adjustment(receipt: ReceiptData) -> list[ReceiptItem]:
    items = list(receipt.items)
    missing_amount = get_receipt_missing_amount(receipt)
    if missing_amount:
        items.append(ReceiptItem(
            name="Unrecognized receipt difference",
            amount=missing_amount,
            category="other",
        ))
    return items


def receipt_expense_rows(receipt: ReceiptData) -> list[dict]:
    return [
        {
            "amount": item.amount,
            "description": item.name,
            "category": item.category,
        }
        for item in receipt_items_with_adjustment(receipt)
    ]


def get_receipt_missing_amount(receipt: ReceiptData) -> float | None:
    if receipt.total is None:
        return None
    missing_amount = round(receipt.total - receipt.items_total, 2)
    return missing_amount if missing_amount > 0.05 else None


def format_receipt_expense_date(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).strftime('%Y-%m-%d')
    except ValueError:
        return value[:10] if len(value) >= 10 else value
