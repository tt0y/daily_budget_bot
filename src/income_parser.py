import re
from dataclasses import dataclass

try:
    from receipt_parser import parse_money
except ImportError:
    from .receipt_parser import parse_money


@dataclass
class ParsedIncome:
    amount: float
    description: str | None


AMOUNT_RE = re.compile(
    r"(?<![\w])(?P<amount>\d+(?:[ .]\d{3})*(?:[,.]\d{1,2})?|\d+(?:[,.]\d{1,2})?)(?![\w])",
    re.IGNORECASE,
)
CURRENCY_RE = re.compile(
    r"(?i)\b(?:евро|eur|euro|euros|руб(?:лей|ля|ль)?|rub|usd|dollars?|доллар(?:ов|а)?)\b|[€$]",
)
INCOME_KEYWORD_RE = re.compile(
    r"(?i)(?:\b(?:income|salary|paycheck|payday|bonus|freelance|earned|received|deposit|transfer|revenue|wage|wages)\b|"
    r"доход|зарплат|зп|аванс|преми|фриланс|перевод|получил|получила|получили|пришло|зачислен|выплат|гонорар)"
)
GENERIC_INCOME_WORDS_RE = re.compile(
    r"(?i)\b(?:income|received|earned|got paid|deposit|transfer)\b|"
    r"доход|перевод|получил|получила|получили|пришло|зачислен[а-я]*|выплат[а-я]*"
)
LEADING_WORDS_RE = re.compile(
    r"(?i)^(?:на|в|во|за|для|по|к|у|от|from|at|in|on|to|for)\s+"
)


def parse_manual_income(text: str | None, require_keyword: bool = True) -> ParsedIncome | None:
    if not text:
        return None

    source = " ".join(text.strip().split())
    if not source:
        return None
    if source.startswith("/") and require_keyword:
        return None
    if require_keyword and not INCOME_KEYWORD_RE.search(source):
        return None

    for match in AMOUNT_RE.finditer(source):
        amount = parse_money(match.group("amount"))
        if amount is None or amount <= 0:
            continue

        return ParsedIncome(
            amount=amount,
            description=_extract_description(source, match, strip_generic=require_keyword),
        )

    return None


def _extract_description(source: str, amount_match: re.Match, strip_generic: bool = True) -> str | None:
    before = source[:amount_match.start()]
    after = source[amount_match.end():]

    after_description = _clean_description(after, strip_generic=strip_generic)
    if after_description:
        return after_description

    before_description = _clean_description(before, strip_generic=strip_generic)
    if before_description:
        return before_description

    return None


def _clean_description(value: str, strip_generic: bool = True) -> str | None:
    text = CURRENCY_RE.sub(" ", value)
    if strip_generic:
        text = GENERIC_INCOME_WORDS_RE.sub(" ", text)
    text = re.sub(r"^[\s:;,.!?-]+|[\s:;,.!?-]+$", "", text)
    text = " ".join(text.split())

    previous = None
    while text and previous != text:
        previous = text
        text = LEADING_WORDS_RE.sub("", text).strip()

    if len(text) < 2:
        return None
    return text[:160]
