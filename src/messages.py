MESSAGES = {
    "en": {
        "welcome_back": "Hello, <b>{name}</b>! Welcome back. Send me your current balance to calculate your daily budget.",
        "welcome_new": "Hello, <b>{name}</b>! Let's set up your profile.",
        "ask_income_day": "Please enter the day of the month you receive your income (1-31):",
        "ask_savings": "Great! Now, what percentage of your income do you NOT plan to spend? (0-100):",
        "settings_saved": "Settings saved! Now send me your current amount of money.",
        "invalid_day": "Please enter a valid day between 1 and 31.",
        "invalid_percent": "Please enter a percentage between 0 and 100.",
        "not_number": "Please enter a number.",
        "start_first": "Please type /start to set up your profile first.",
        "invalid_balance": "Please enter a valid number for your current balance.",
        "financial_plan": "💰 <b>Financial Plan</b>\nNext Income Date: {next_income}\nDays Remaining: {days_remaining}\nSavings ({savings_percent}%): {savings_amount}\nAvailable to Spend: {safe_to_spend}\n<b>Daily Budget: {daily_budget}</b>",
        "update_settings": "Let's update your settings.\nPlease enter the day of the month you receive your income (1-31):",
        "help_text": (
            "This bot helps you plan your daily budget.\n\n"
            "1. You set your <b>Income Day</b> and <b>Savings Percentage</b>.\n"
            "2. You send me your <b>Current Balance</b>.\n"
            "3. I calculate how much you can spend per day until your next income, saving the specified percentage.\n\n"
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
        "btn_ru": "🇷🇺 Русский"
    },
    "ru": {
        "welcome_back": "Привет, <b>{name}</b>! С возвращением. Отправь мне текущий баланс, чтобы рассчитать дневной бюджет.",
        "welcome_new": "Привет, <b>{name}</b>! Давай настроим твой профиль.",
        "ask_income_day": "Пожалуйста, введи день месяца, когда ты получаешь доход (1-31):",
        "ask_savings": "Отлично! Теперь какой процент дохода ты НЕ планируешь тратить? (0-100):",
        "settings_saved": "Настройки сохранены! Теперь отправь мне текущую сумму денег.",
        "invalid_day": "Пожалуйста, введи корректный день от 1 до 31.",
        "invalid_percent": "Пожалуйста, введи процент от 0 до 100.",
        "not_number": "Пожалуйста, введи число.",
        "start_first": "Пожалуйста, введи /start, чтобы сначала настроить профиль.",
        "invalid_balance": "Пожалуйста, введи корректное число для текущего баланса.",
        "financial_plan": "💰 <b>Финансовый план</b>\nДата следующего дохода: {next_income}\nОсталось дней: {days_remaining}\nСбережения ({savings_percent}%): {savings_amount}\nДоступно для трат: {safe_to_spend}\n<b>Дневной бюджет: {daily_budget}</b>",
        "update_settings": "Давай обновим настройки.\nПожалуйста, введи день месяца, когда ты получаешь доход (1-31):",
        "help_text": (
            "Этот бот помогает планировать дневной бюджет.\n\n"
            "1. Ты указываешь <b>День дохода</b> и <b>Процент сбережений</b>.\n"
            "2. Ты отправляешь мне <b>Текущий баланс</b>.\n"
            "3. Я рассчитываю, сколько можно тратить в день до следующего дохода, с учетом сбережений.\n\n"
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
        "btn_ru": "🇷🇺 Русский"
    }
}

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """Get localized text."""
    lang_dict = MESSAGES.get(lang, MESSAGES["en"])
    text = lang_dict.get(key, MESSAGES["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text
