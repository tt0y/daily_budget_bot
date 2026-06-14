import re
from dataclasses import dataclass

try:
    from receipt_parser import normalize_category, parse_money
except ImportError:
    from .receipt_parser import normalize_category, parse_money


@dataclass
class ParsedExpense:
    amount: float
    description: str
    category: str


CATEGORY_KEYWORDS = {
    "pet_project": (
        "pet-project", "pet project", "side project", "side-project",
        "пет-проект", "пет проект", "сайд-проект", "сайд проект",
    ),
    "groceries": (
        "fruit", "fruits", "vegetable", "vegetables", "grocery", "groceries",
        "supermarket", "food", "water", "beer", "bread", "milk", "cheese",
        "meat", "fish", "фрукт", "овощ", "продукт", "еда", "вода", "пиво",
        "хлеб", "молок", "сыр", "мяс", "рыб",
    ),
    "beauty": (
        "hair", "haircut", "barber", "beauty", "salon", "manicure",
        "парикмах", "стриж", "барбер", "салон", "маникюр", "космет",
    ),
    "subscriptions": (
        "hosting", "host", "domain", "server", "vps", "cloud", "subscription",
        "netflix", "spotify", "openai", "хостинг", "домен", "сервер",
        "подписк", "облак",
    ),
    "education": (
        "stationery", "notebook", "pen", "pencil", "office supplies",
        "канцел", "тетрад", "ручк", "карандаш", "бумаг",
    ),
    "transport": (
        "taxi", "bus", "metro", "train", "fuel", "gas", "parking",
        "такси", "автобус", "метро", "поезд", "бензин", "парков",
    ),
    "cafe": (
        "cafe", "coffee", "restaurant", "lunch", "dinner", "кафе", "кофе",
        "ресторан", "обед", "ужин",
    ),
    "health": (
        "pharmacy", "doctor", "dentist", "medicine", "аптек", "врач",
        "доктор", "стоматолог", "лекарств",
    ),
    "home": (
        "rent", "utilities", "cleaning", "repair", "ikea", "home",
        "аренд", "коммун", "уборк", "ремонт", "дом",
    ),
    "tech": (
        "phone", "laptop", "computer", "gadget", "software", "телефон",
        "ноутбук", "комп", "гаджет", "софт",
    ),
    "clothes": (
        "clothes", "shoes", "shirt", "dress", "одежд", "обув", "футболк",
        "плать",
    ),
    "books": (
        "book", "books", "книг",
    ),
    "sport": (
        "gym", "fitness", "sport", "зал", "спорт", "фитнес",
    ),
    "charity": (
        "charity", "donation", "donate", "благотвор", "донат",
    ),
}

AMOUNT_RE = re.compile(
    r"(?<![\w])(?P<amount>\d+(?:[ .]\d{3})*(?:[,.]\d{1,2})?|\d+(?:[,.]\d{1,2})?)(?![\w])",
    re.IGNORECASE,
)
CURRENCY_RE = re.compile(
    r"(?i)\b(?:евро|eur|euro|euros|руб(?:лей|ля|ль)?|rub|usd|dollars?|доллар(?:ов|а)?)\b|[€$]",
)
LEADING_WORDS_RE = re.compile(
    r"(?i)^(?:на|в|во|за|для|по|к|у|at|in|on|to|for)\s+"
)


def parse_manual_expense(text: str | None) -> ParsedExpense | None:
    if not text:
        return None

    source = " ".join(text.strip().split())
    if not source or source.startswith("/"):
        return None

    for match in AMOUNT_RE.finditer(source):
        amount = parse_money(match.group("amount"))
        if amount is None or amount <= 0:
            continue

        description = _extract_description(source, match)
        if not description:
            continue

        return ParsedExpense(
            amount=amount,
            description=description,
            category=categorize_expense(description),
        )

    return None


def categorize_expense(description: str) -> str:
    lowered = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return normalize_category(category)
    return "other"


def _extract_description(source: str, amount_match: re.Match) -> str | None:
    before = source[:amount_match.start()]
    after = source[amount_match.end():]

    after_description = _clean_description(after)
    if after_description:
        return after_description

    before_description = _clean_description(before)
    if before_description:
        return before_description

    return None


def _clean_description(value: str) -> str | None:
    text = CURRENCY_RE.sub(" ", value)
    text = re.sub(r"^[\s:;,.!?-]+|[\s:;,.!?-]+$", "", text)
    text = " ".join(text.split())

    previous = None
    while text and previous != text:
        previous = text
        text = LEADING_WORDS_RE.sub("", text).strip()

    if len(text) < 2:
        return None
    return text[:160]
