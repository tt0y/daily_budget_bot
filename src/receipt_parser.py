import base64
import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from io import BytesIO
from typing import Iterable


@dataclass(frozen=True)
class BudgetCategory:
    id: str
    en: str
    ru: str


CATEGORIES = [
    BudgetCategory("health", "Health", "Здоровье"),
    BudgetCategory("leisure", "Leisure", "Досуг"),
    BudgetCategory("home", "Home", "Дом"),
    BudgetCategory("cafe", "Cafe", "Кафе"),
    BudgetCategory("education", "Education", "Образование"),
    BudgetCategory("gifts", "Gifts", "Подарки"),
    BudgetCategory("groceries", "Groceries", "Продукты"),
    BudgetCategory("family", "Family", "Семья"),
    BudgetCategory("sport", "Sport", "Спорт"),
    BudgetCategory("transport", "Transport", "Транспорт"),
    BudgetCategory("other", "Other", "Другое"),
    BudgetCategory("taxes", "Taxes", "Налоги"),
    BudgetCategory("beauty", "Beauty", "Красота"),
    BudgetCategory("hobby", "Hobby", "Хобби"),
    BudgetCategory("tech", "Tech", "Техника"),
    BudgetCategory("books", "Books", "Книги"),
    BudgetCategory("unknown", "Unknown", "Не помню"),
    BudgetCategory("entertainment", "Entertainment", "Развлечения"),
    BudgetCategory("subscriptions", "Subscriptions", "Подписки"),
    BudgetCategory("credits", "Credits", "Кредиты"),
    BudgetCategory("clothes", "Clothes", "Одежда"),
    BudgetCategory("charity", "Charity", "Благотворительность"),
]

CATEGORY_IDS = {category.id for category in CATEGORIES}
CATEGORY_BY_ID = {category.id: category for category in CATEGORIES}
CATEGORY_ALIASES = {
    category.id.lower(): category.id
    for category in CATEGORIES
}
CATEGORY_ALIASES.update({
    category.en.lower(): category.id
    for category in CATEGORIES
})
CATEGORY_ALIASES.update({
    category.ru.lower(): category.id
    for category in CATEGORIES
})
CATEGORY_ALIASES.update({
    "food": "groceries",
    "products": "groceries",
    "supermarket": "groceries",
    "продукты": "groceries",
    "еда": "groceries",
    "магазин": "groceries",
    "restaurant": "cafe",
    "restaurants": "cafe",
    "coffee": "cafe",
    "кафе": "cafe",
    "ресторан": "cafe",
    "household": "home",
    "дом": "home",
    "быт": "home",
    "cosmetics": "beauty",
    "косметика": "beauty",
    "unknown": "unknown",
    "не помню": "unknown",
})

SUPPORTED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
}
SUPPORTED_DOCUMENT_MIME_TYPES = SUPPORTED_IMAGE_MIME_TYPES | {"application/pdf"}
SUPPORTED_IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")


class ReceiptParserError(Exception):
    """Raised when a receipt cannot be parsed into a useful structure."""


class ReceiptParserUnavailable(ReceiptParserError):
    """Raised when receipt parsing is not configured."""


@dataclass
class ReceiptItem:
    name: str
    amount: float
    category: str
    quantity: float | None = None
    confidence: float | None = None


@dataclass
class ReceiptData:
    merchant: str | None
    purchased_at: str | None
    currency: str
    total: float | None
    items: list[ReceiptItem]
    notes: list[str]

    @property
    def items_total(self) -> float:
        return round(sum(item.amount for item in self.items), 2)


def category_label(category_id: str, lang: str = "en") -> str:
    category = CATEGORY_BY_ID.get(category_id, CATEGORY_BY_ID["other"])
    return category.ru if lang == "ru" else category.en


def is_supported_receipt_file(mime_type: str | None, filename: str | None = None) -> bool:
    mime_type = (mime_type or "").lower()
    filename = (filename or "").lower()
    return (
        mime_type in SUPPORTED_DOCUMENT_MIME_TYPES
        or filename.endswith(".pdf")
        or filename.endswith(SUPPORTED_IMAGE_EXTENSIONS)
    )


def normalize_category(value: str | None) -> str:
    if not value:
        return "other"
    key = str(value).strip().lower()
    return CATEGORY_ALIASES.get(key, key if key in CATEGORY_IDS else "other")


def parse_money(value) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return round(float(value), 2)

    text = str(value).strip()
    if not text:
        return None

    text = text.replace("€", "").replace("$", "").replace("\u00a0", " ").strip()
    text = re.sub(r"[^\d,.\-]", "", text)
    if not text or text in {"-", ".", ","}:
        return None

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(",", ".")

    try:
        return round(float(text), 2)
    except ValueError:
        return None


def _parse_quantity(value) -> float | None:
    money = parse_money(value)
    if money is None:
        return None
    return money


def parse_receipt_response(content: str | dict) -> ReceiptData:
    payload = content if isinstance(content, dict) else _loads_json_object(content)
    items = []

    for raw_item in payload.get("items", []):
        if not isinstance(raw_item, dict):
            continue
        amount = parse_money(raw_item.get("amount"))
        name = str(raw_item.get("name") or raw_item.get("description") or "").strip()
        if not name or amount is None or amount <= 0:
            continue

        confidence = raw_item.get("confidence")
        try:
            confidence = float(confidence) if confidence is not None else None
        except (TypeError, ValueError):
            confidence = None

        items.append(ReceiptItem(
            name=name[:160],
            quantity=_parse_quantity(raw_item.get("quantity")),
            amount=amount,
            category=normalize_category(raw_item.get("category")),
            confidence=confidence,
        ))

    total = parse_money(payload.get("total"))
    if total is None and items:
        total = round(sum(item.amount for item in items), 2)

    notes = payload.get("notes") or []
    if not isinstance(notes, list):
        notes = [str(notes)]

    currency = str(payload.get("currency") or "EUR").strip().upper()
    if not currency:
        currency = "EUR"

    purchased_at = payload.get("purchased_at")
    purchased_at = normalize_datetime(purchased_at)

    merchant = payload.get("merchant")
    if merchant is not None:
        merchant = str(merchant).strip()[:120] or None

    return ReceiptData(
        merchant=merchant,
        purchased_at=purchased_at,
        currency=currency[:8],
        total=total,
        items=items,
        notes=[str(note).strip() for note in notes if str(note).strip()],
    )


def summarize_categories(items: Iterable[ReceiptItem]) -> list[tuple[str, float, int]]:
    totals: dict[str, tuple[float, int]] = {}
    for item in items:
        amount, count = totals.get(item.category, (0.0, 0))
        totals[item.category] = (amount + item.amount, count + 1)
    return [
        (category_id, round(amount, 2), count)
        for category_id, (amount, count) in sorted(
            totals.items(),
            key=lambda entry: (-entry[1][0], category_label(entry[0], "ru")),
        )
    ]


def normalize_datetime(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    text = text.replace("/", "-")
    formats = (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%d-%m-%Y %H:%M:%S",
        "%d-%m-%Y %H:%M",
        "%d-%m-%Y",
        "%m-%d-%Y %I:%M %p",
        "%m-%d-%Y %H:%M:%S",
        "%m-%d-%Y",
    )
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt).isoformat(timespec='seconds')
        except ValueError:
            pass

    try:
        return datetime.fromisoformat(text).isoformat(timespec='seconds')
    except ValueError:
        return None


async def parse_receipt_file(file_bytes: bytes, mime_type: str, filename: str | None = None) -> ReceiptData:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ReceiptParserUnavailable("OPENAI_API_KEY is not configured")

    content = await _call_openai_receipt_parser(file_bytes, mime_type, filename)
    receipt = parse_receipt_response(content)
    if not receipt.items:
        raise ReceiptParserError("No receipt items were recognized")
    return receipt


async def _call_openai_receipt_parser(file_bytes: bytes, mime_type: str, filename: str | None) -> str:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model = os.getenv("OPENAI_RECEIPT_MODEL", "gpt-4o-mini")
    image_parts = _build_image_parts(file_bytes, mime_type, filename)

    response = await client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You parse grocery/shop receipts from images or rendered PDF pages. "
                    "Extract real purchased line items only. Exclude payment lines, tax summaries, "
                    "barcodes, store legal text, card data, subtotals, and duplicate totals."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": _receipt_prompt(filename)},
                    *image_parts,
                ],
            },
        ],
        temperature=0,
    )
    return response.choices[0].message.content or "{}"


def _receipt_prompt(filename: str | None) -> str:
    categories = "\n".join(
        f"- {category.id}: {category.en} / {category.ru}"
        for category in CATEGORIES
    )
    return (
        f"Filename: {filename or 'unknown'}\n\n"
        "Return one JSON object with this exact shape:\n"
        "{\n"
        '  "merchant": string|null,\n'
        '  "purchased_at": "YYYY-MM-DDTHH:MM:SS"|null,\n'
        '  "currency": "EUR"|"...",\n'
        '  "total": number|null,\n'
        '  "items": [\n'
        '    {"name": string, "quantity": number|null, "amount": number, '
        '"category": string, "confidence": number}\n'
        "  ],\n"
        '  "notes": [string]\n'
        "}\n\n"
        "Rules:\n"
        "- Use decimal points, not commas.\n"
        "- `amount` is the final line amount for the item, not unit price.\n"
        "- Preserve concise item names as printed, correcting obvious OCR mistakes.\n"
        "- If the receipt has several pages, merge them into one receipt.\n"
        "- If a line is ambiguous but likely an item, include it with lower confidence.\n"
        "- Use one of these category ids only:\n"
        f"{categories}\n\n"
        "Category hints: supermarket food/drinks/alcohol/water => groceries; "
        "soap, toilet paper, cleaning, reusable cups, home supplies => home; "
        "cosmetics/personal care => beauty; restaurant/coffee bar => cafe; "
        "medicine/pharmacy => health; electronics/games/devices => tech; "
        "if truly impossible, use unknown."
    )


def _build_image_parts(file_bytes: bytes, mime_type: str, filename: str | None) -> list[dict]:
    mime_type = (mime_type or "").lower()
    filename = (filename or "").lower()
    if mime_type == "application/pdf" or filename.endswith(".pdf"):
        images = _pdf_to_jpeg_data_urls(file_bytes)
    elif mime_type in SUPPORTED_IMAGE_MIME_TYPES or filename.endswith(SUPPORTED_IMAGE_EXTENSIONS):
        images = [_image_to_jpeg_data_url(file_bytes)]
    else:
        raise ReceiptParserError(f"Unsupported receipt file type: {mime_type or 'unknown'}")

    return [
        {"type": "image_url", "image_url": {"url": data_url}}
        for data_url in images
    ]


def _image_to_jpeg_data_url(file_bytes: bytes, max_side: int = 2200, quality: int = 86) -> str:
    from PIL import Image, ImageOps

    with Image.open(BytesIO(file_bytes)) as image:
        image = ImageOps.exif_transpose(image)
        if image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")
        if image.mode == "L":
            image = image.convert("RGB")

        width, height = image.size
        longest = max(width, height)
        if longest > max_side:
            scale = max_side / longest
            image = image.resize((int(width * scale), int(height * scale)))

        output = BytesIO()
        image.save(output, format="JPEG", quality=quality, optimize=True)
        encoded = base64.b64encode(output.getvalue()).decode("ascii")
        return f"data:image/jpeg;base64,{encoded}"


def _pdf_to_jpeg_data_urls(file_bytes: bytes, max_pages: int = 3) -> list[str]:
    import fitz

    urls = []
    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page_number in range(min(len(document), max_pages)):
            page = document[page_number]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            urls.append(_image_to_jpeg_data_url(pixmap.tobytes("png")))

    if not urls:
        raise ReceiptParserError("PDF has no pages")
    return urls


def _loads_json_object(content: str) -> dict:
    text = (content or "").strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text, flags=re.IGNORECASE).strip()
        text = re.sub(r"```$", "", text).strip()

    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ReceiptParserError("Receipt parser did not return JSON")
        payload = json.loads(text[start:end + 1])

    if not isinstance(payload, dict):
        raise ReceiptParserError("Receipt parser returned a non-object JSON value")
    return payload
