MESSAGES = {
    "en": {
        "welcome_back": "Hello, <b>{name}</b>! Welcome back. Send me your current balance to calculate your daily budget.",
        "welcome_new": "Hello, <b>{name}</b>! Let's set up your profile.",
        "ask_income_day": "Please enter the day of the month you receive your income (1-31):",
        "ask_monthly_income": "What is your expected monthly income?",
        "ask_savings": "Great! Now, what percentage of your income do you NOT plan to spend? (0-100):",
        "settings_saved": "Settings saved! Now send me your current amount of money.",
        "invalid_day": "Please enter a valid day between 1 and 31.",
        "invalid_income": "Please enter a valid number for your income.",
        "invalid_percent": "Please enter a percentage between 0 and 100.",
        "not_number": "Please enter a number.",
        "start_first": "Please type /start to set up your profile first or complete your settings.",
        "settings_incomplete": "Your settings are incomplete. Please use /settings to add your monthly income.",
        "invalid_balance": "Please enter a valid number for your current balance.",
        "financial_plan": "💰 <b>Financial Plan</b>\nNext Income Date: {next_income}\nDays Remaining: {days_remaining}\nSavings ({savings_percent}% of {monthly_income}): {savings_amount}\nAvailable to Spend: {safe_to_spend}\n<b>Daily Budget: {daily_budget}</b>",
        "update_settings": "Let's update your settings.\nPlease enter the day of the month you receive your income (1-31):",
        "help_text": (
            "This bot helps you plan your daily budget.\n\n"
            "1. You set your <b>Income Day</b>, <b>Monthly Income</b> and <b>Savings Percentage</b>.\n"
            "2. You send me your <b>Current Balance</b>.\n"
            "3. I calculate how much you can spend per day until your next income, subtracting your target savings goal.\n"
            "4. Send your balance regularly and I'll also forecast how long your money will last at your current spending pace.\n\n"
            "Commands:\n"
            "/start - Initialize or update settings\n"
            "/balance &lt;amount&gt; - Calculate budget for a specific balance\n"
            "/settings - Change your settings\n"
            "/language - Change language / Сменить язык\n"
            "/help - Show this help message"
        ),
        "provide_balance_args": "Please provide a valid number, e.g., /balance 1000",
        "provide_balance": "Please provide your balance, e.g., /balance 1000",
        "invalid_format": "Invalid format.",
        "reminder": "Good morning! ☀️\nWhat is your current balance today? Send it to me to update your budget.",
        "choose_language": "Please choose your language / Пожалуйста, выберите язык:",
        "language_set": "Language set to English.",
        "btn_en": "🇬🇧 English",
        "btn_ru": "🇷🇺 Русский",
        "trend_line": "💸 At your current pace (~{rate}/day) the money will last about {days} more {days_word}.",
        "trend_less_than_day": "💸 At your current pace (~{rate}/day) the money won't last another full day.",
        "trend_ok": "✅ That covers the {days} {days_word} until your next income.",
        "trend_risk": "⚠️ That's less than the {days} {days_word} until your next income — you risk going negative.",
        "trend_no_data": "📊 Not enough data for a trend yet — send one more balance reading and I'll estimate the dynamics.",
        "trend_no_spending": "📊 Your balance isn't dropping — no spending detected yet.",
        "trend_depleted": "⚠️ At the current balance the money has already run out."
    },
    "ru": {
        "welcome_back": "Привет, <b>{name}</b>! С возвращением. Отправь мне текущий баланс, чтобы рассчитать дневной бюджет.",
        "welcome_new": "Привет, <b>{name}</b>! Давай настроим твой профиль.",
        "ask_income_day": "Пожалуйста, введи день месяца, когда ты получаешь доход (1-31):",
        "ask_monthly_income": "Каков твой ожидаемый ежемесячный доход?",
        "ask_savings": "Отлично! Теперь какой процент дохода ты НЕ планируешь тратить? (0-100):",
        "settings_saved": "Настройки сохранены! Теперь отправь мне текущую сумму денег.",
        "invalid_day": "Пожалуйста, введи корректный день от 1 до 31.",
        "invalid_income": "Пожалуйста, введи корректное число для дохода.",
        "invalid_percent": "Пожалуйста, введи процент от 0 до 100.",
        "not_number": "Пожалуйста, введи число.",
        "start_first": "Пожалуйста, введи /start, чтобы сначала настроить профиль.",
        "settings_incomplete": "Настройки не завершены. Пожалуйста, используй /settings, чтобы добавить ежемесячный доход.",
        "invalid_balance": "Пожалуйста, введи корректное число для текущего баланса.",
        "financial_plan": "💰 <b>Финансовый план</b>\nДата следующего дохода: {next_income}\nОсталось дней: {days_remaining}\nСбережения ({savings_percent}% от {monthly_income}): {savings_amount}\nДоступно для трат: {safe_to_spend}\n<b>Дневной бюджет: {daily_budget}</b>",
        "update_settings": "Давай обновим настройки.\nПожалуйста, введи день месяца, когда ты получаешь доход (1-31):",
        "help_text": (
            "Этот бот помогает планировать дневной бюджет.\n\n"
            "1. Ты указываешь <b>День дохода</b>, <b>Ежемесячный доход</b> и <b>Процент сбережений</b>.\n"
            "2. Ты отправляешь мне <b>Текущий баланс</b>.\n"
            "3. Я рассчитываю, сколько можно тратить в день до следующего дохода, вычитая целевые сбережения.\n"
            "4. Присылай баланс регулярно — и я ещё спрогнозирую, на сколько хватит денег при текущем темпе трат.\n\n"
            "Команды:\n"
            "/start - Начать или изменить настройки\n"
            "/balance &lt;сумма&gt; - Рассчитать бюджет для конкретной суммы\n"
            "/settings - Изменить настройки\n"
            "/language - Change language / Сменить язык\n"
            "/help - Показать это сообщение"
        ),
        "provide_balance_args": "Пожалуйста, укажи число, например, /balance 1000",
        "provide_balance": "Пожалуйста, укажи баланс, например, /balance 1000",
        "invalid_format": "Неверный формат.",
        "reminder": "Доброе утро! ☀️\nКакой у тебя сегодня баланс? Отправь его мне, чтобы обновить бюджет.",
        "choose_language": "Please choose your language / Пожалуйста, выберите язык:",
        "language_set": "Язык установлен на Русский.",
        "btn_en": "🇬🇧 English",
        "btn_ru": "🇷🇺 Русский",
        "trend_line": "💸 При текущем темпе (~{rate}/день) денег хватит ещё примерно на {days} {days_word}.",
        "trend_less_than_day": "💸 При текущем темпе (~{rate}/день) денег не хватит даже на день.",
        "trend_ok": "✅ Этого хватит до следующего дохода ({days} {days_word}).",
        "trend_risk": "⚠️ Это меньше, чем {days} {days_word} до следующего дохода — рискуешь уйти в минус.",
        "trend_no_data": "📊 Пока мало данных для тренда — пришли ещё одно значение баланса, и я оценю динамику.",
        "trend_no_spending": "📊 Баланс не снижается — расходов пока не вижу.",
        "trend_depleted": "⚠️ При текущем балансе денег уже не осталось."
    }
}

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Get localized text."""
    lang_dict = MESSAGES.get(lang, MESSAGES["en"])
    text = lang_dict.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def _days_word(n: int, lang: str = "en") -> str:
    """Correct word form for a number of days."""
    n = abs(int(n))
    if lang == "ru":
        if n % 10 == 1 and n % 100 != 11:
            return "день"
        if 2 <= n % 10 <= 4 and not (12 <= n % 100 <= 14):
            return "дня"
        return "дней"
    return "day" if n == 1 else "days"


def get_trend_text(runway: dict, days_remaining: int, lang: str = "en") -> str:
    """Build the spending-trend block from an estimate_runway() result.

    Returns an empty string when there is nothing meaningful to show.
    """
    reason = runway.get("reason")

    if reason == "insufficient_history":
        return get_text("trend_no_data", lang)
    if reason == "no_spending":
        return get_text("trend_no_spending", lang)
    if reason == "depleted":
        return get_text("trend_depleted", lang)
    if not runway.get("has_estimate"):
        return ""

    rate = f"{runway['daily_spend']:.2f}"
    days_left = runway["days_left"]
    days_int = int(days_left)  # floor: the money lasts at least this many full days

    if days_int < 1:
        line = get_text("trend_less_than_day", lang, rate=rate)
    else:
        line = get_text("trend_line", lang, rate=rate, days=days_int, days_word=_days_word(days_int, lang))

    # Verdict: does the current pace carry the user to the next income?
    verdict = ""
    if days_remaining and days_remaining > 0:
        if days_left + 1e-9 >= days_remaining:
            verdict = get_text("trend_ok", lang, days=days_remaining, days_word=_days_word(days_remaining, lang))
        else:
            verdict = get_text("trend_risk", lang, days=days_remaining, days_word=_days_word(days_remaining, lang))

    return f"{line}\n{verdict}".strip() if verdict else line
