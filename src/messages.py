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
            "5. Send a receipt photo/PDF and I'll split its items into spending categories.\n\n"
            "Examples:\n"
            "• Send <code>1000</code> or <code>/balance 1000</code> to update your current balance.\n"
            "• Send <code>/income 3000 salary</code> or <code>salary 3000</code> to save income.\n"
            "• Send <code>20 euro at the barber</code> or <code>10 euro for pet-project hosting</code> to save a manual expense.\n"
            "• Send a receipt as a photo, image file, or PDF to save its itemized expenses.\n"
            "• Send <code>/stats</code> to see expenses added today.\n"
            "• Send <code>/stats month</code> to see the current month by expense date.\n"
            "• Send <code>/stats year</code> to see the current year by expense date.\n"
            "• Send <code>/stats all</code> to see all saved expenses.\n\n"
            "Commands:\n"
            "/start - Initialize or update settings\n"
            "/balance &lt;amount&gt; - Calculate budget for a specific balance\n"
            "/income &lt;amount&gt; [description] - Save an income entry\n"
            "/stats [month|year|all] - Show saved expenses grouped by category\n"
            "/stats_month - Show the current month\n"
            "/stats_year - Show the current year\n"
            "/stats_all - Show all saved expenses\n"
            "/family - Show your family budget\n"
            "/family_invite - Create an invite code\n"
            "/family_join &lt;code&gt; - Join a family budget\n"
            "/settings - Change your settings\n"
            "/language - Change language / Сменить язык\n"
            "/help - Show this help message"
        ),
        "provide_balance_args": "Please provide a valid number, e.g., /balance 1000",
        "provide_balance": "Please provide your balance, e.g., /balance 1000",
        "provide_income_args": "Please provide a valid income, e.g., <code>/income 3000 salary</code>",
        "provide_income": "Please provide an income amount, e.g., <code>/income 3000 salary</code>",
        "income_default_description": "Income",
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
        "trend_depleted": "⚠️ At the current balance the money has already run out.",
        "receipt_processing": "I’m reading the receipt and sorting items into categories...",
        "receipt_parser_unavailable": "Receipt parsing is not configured yet. Add OPENAI_API_KEY to the bot environment and restart it.",
        "receipt_parse_failed": "I couldn't read this receipt clearly. Please try a sharper photo or a PDF.",
        "receipt_unsupported_file": "Please send a receipt as a photo, image file, or PDF.",
        "receipt_unknown_store": "Unknown store",
        "receipt_date_saved": "Recorded on receipt date: <b>{date}</b>.",
        "receipt_date_fallback": "Receipt date was not recognized, so I recorded expenses on the upload date.",
        "receipt_saved": "✅ Receipt saved: <b>{merchant}</b>\nTotal: <b>{total} {currency}</b>\nItems: <b>{count}</b>",
        "receipt_categories_header": "<b>By category:</b>",
        "receipt_items_header": "<b>Recognized items:</b>",
        "receipt_more_items": "...and {count} more",
        "receipt_total_adjusted": "I added the missing <b>{amount}</b> to <b>Other</b> so categories match the receipt total.",
        "receipt_total_mismatch": "Check the total: items add up to {items_total}, receipt total is {receipt_total}.",
        "stats_header_added_today": "📊 <b>Added today</b>",
        "stats_header_expense_month": "📊 <b>Current month by expense date</b>",
        "stats_header_expense_year": "📊 <b>Current year by expense date</b>",
        "stats_header_all": "📊 <b>All saved expenses</b>",
        "stats_empty_added_today": "No expenses were added today yet.",
        "stats_empty_expense_month": "No expenses with dates in the current month yet.",
        "stats_empty_expense_year": "No expenses with dates in the current year yet.",
        "stats_empty_all": "No expenses saved yet.",
        "stats_total": "<b>Total: {amount}</b>",
        "stats_usage": "Use <code>/stats</code>, <code>/stats month</code>, <code>/stats year</code>, or <code>/stats all</code>.",
        "family_info": "<b>Family budget</b>\nBudget: <b>{name}</b>\nMembers: <b>{count}</b>\n\n{members}\n\nUse <code>/family_invite</code> to invite someone.",
        "family_invite_created": "Share this code with another person:\n<code>{code}</code>\n\nThey can join with:\n<code>/family_join {code}</code>",
        "family_join_usage": "Send an invite code like this:\n<code>/family_join ABCD2345</code>",
        "family_join_invalid": "I couldn't find a family budget with that invite code.",
        "family_joined": "✅ Joined family budget: <b>{name}</b>.\nFrom now on, your expenses, receipts, stats, and balance readings use this shared budget.",
        "family_no_members": "No members yet.",
        "family_role_owner": "owner",
        "family_role_member": "member",
        "unsupported_message": "Send me a number for your current balance, income like <code>salary 3000</code>, a manual expense like <code>20 euro at the barber</code>, or a receipt photo/PDF.",
        "manual_income_added": "✅ Income saved: <b>{amount}</b>\nDescription: {description}",
        "manual_expense_added": "✅ Expense saved: <b>{amount}</b>\nCategory: <b>{category}</b>\nDescription: {description}",
        "btn_stats_today": "📊 Today's stats",
        "btn_stats_month": "📅 Month",
        "btn_stats_year": "Year",
        "btn_stats_all": "All",
        "btn_menu_balance": "💰 Balance",
        "btn_menu_income": "Income",
        "btn_menu_expense": "✍️ Expense",
        "btn_menu_receipt": "🧾 Receipt",
        "btn_menu_stats": "📊 Stats",
        "btn_menu_settings": "⚙️ Settings",
        "btn_menu_language": "🌐 Language",
        "btn_menu_family": "Family",
        "btn_menu_back": "Back",
        "btn_settings_start": "Change settings",
        "btn_receipt_help": "🧾 Receipt example",
        "btn_expense_help": "✍️ Expense example",
        "btn_balance_help": "💰 Balance example",
        "menu_main_text": (
            "<b>Main menu</b>\n\n"
            "Choose what you want to do:"
        ),
        "menu_stats_text": (
            "<b>Stats</b>\n\n"
            "Choose a period:\n"
            "• Today - expenses added today.\n"
            "• Month - current month by expense date.\n"
            "• Year - current year by expense date.\n"
            "• All - everything saved."
        ),
        "menu_settings_text": (
            "<b>Settings</b>\n\n"
            "Update income day, expected monthly income, and savings percentage."
        ),
        "menu_language_text": (
            "<b>Language</b>\n\n"
            "Choose the bot language:"
        ),
        "help_receipt_example": (
            "Send a receipt as a regular photo, image file, or PDF.\n\n"
            "I will extract line items, assign each one to a category, save them as expenses, "
            "and show a summary by category."
        ),
        "help_income_example": (
            "Save income with a command:\n"
            "<code>/income 3000 salary</code>\n"
            "<code>/income 500 freelance</code>\n\n"
            "Or send a short text with an income hint:\n"
            "<code>salary 3000</code>\n"
            "<code>received 500 from client</code>"
        ),
        "help_expense_example": (
            "Send a short expense in plain text:\n"
            "<code>20 euro at the barber</code>\n"
            "<code>10 euro for pet-project hosting</code>\n"
            "<code>5 euro for fruit</code>\n\n"
            "I will save it today and choose the closest category."
        ),
        "help_balance_example": (
            "Send your balance as a plain number:\n"
            "<code>1000</code>\n\n"
            "Or as a command:\n"
            "<code>/balance 1000</code>"
        )
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
            "5. Пришли фото/PDF чека — я разложу позиции по категориям расходов.\n\n"
            "Примеры:\n"
            "• Пришли <code>1000</code> или <code>/balance 1000</code>, чтобы обновить текущий баланс.\n"
            "• Пришли <code>/income 3000 зарплата</code> или <code>зарплата 3000</code>, чтобы сохранить доход.\n"
            "• Пришли <code>20 евро в парикмахерской</code> или <code>10 евро на хостинг пет-проекта</code>, чтобы сохранить ручной расход.\n"
            "• Пришли чек обычным фото, файлом-картинкой или PDF — я сохраню позиции как расходы.\n"
            "• Пришли <code>/stats</code>, чтобы увидеть расходы, добавленные сегодня.\n"
            "• Пришли <code>/stats month</code>, чтобы увидеть текущий месяц по датам расходов.\n"
            "• Пришли <code>/stats year</code>, чтобы увидеть текущий год по датам расходов.\n"
            "• Пришли <code>/stats all</code>, чтобы увидеть все сохраненные расходы.\n\n"
            "Команды:\n"
            "/start - Начать или изменить настройки\n"
            "/balance &lt;сумма&gt; - Рассчитать бюджет для конкретной суммы\n"
            "/income &lt;сумма&gt; [описание] - Сохранить доход\n"
            "/stats [month|year|all] - Сохраненные расходы по категориям\n"
            "/stats_month - Статистика за текущий месяц\n"
            "/stats_year - Статистика за текущий год\n"
            "/stats_all - Все сохраненные расходы\n"
            "/family - Семейный бюджет\n"
            "/family_invite - Создать код приглашения\n"
            "/family_join &lt;код&gt; - Присоединиться к семейному бюджету\n"
            "/settings - Изменить настройки\n"
            "/language - Change language / Сменить язык\n"
            "/help - Показать это сообщение"
        ),
        "provide_balance_args": "Пожалуйста, укажи число, например, /balance 1000",
        "provide_balance": "Пожалуйста, укажи баланс, например, /balance 1000",
        "provide_income_args": "Пожалуйста, укажи корректный доход, например, <code>/income 3000 зарплата</code>",
        "provide_income": "Пожалуйста, укажи сумму дохода, например, <code>/income 3000 зарплата</code>",
        "income_default_description": "Доход",
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
        "trend_depleted": "⚠️ При текущем балансе денег уже не осталось.",
        "receipt_processing": "Распознаю чек и раскладываю позиции по категориям...",
        "receipt_parser_unavailable": "Распознавание чеков ещё не настроено. Добавь OPENAI_API_KEY в окружение бота и перезапусти его.",
        "receipt_parse_failed": "Не смог уверенно прочитать этот чек. Попробуй более четкое фото или PDF.",
        "receipt_unsupported_file": "Пришли чек как фото, файл-картинку или PDF.",
        "receipt_unknown_store": "Магазин не распознан",
        "receipt_date_saved": "Расходы записаны на дату чека: <b>{date}</b>.",
        "receipt_date_fallback": "Дату на чеке не распознал, поэтому записал расходы на дату загрузки.",
        "receipt_saved": "✅ Чек сохранен: <b>{merchant}</b>\nИтого: <b>{total} {currency}</b>\nПозиций: <b>{count}</b>",
        "receipt_categories_header": "<b>По категориям:</b>",
        "receipt_items_header": "<b>Распознанные позиции:</b>",
        "receipt_more_items": "...и еще {count}",
        "receipt_total_adjusted": "Разницу <b>{amount}</b> добавил в <b>Другое</b>, чтобы категории сошлись с итогом чека.",
        "receipt_total_mismatch": "Проверь сумму: позиции дают {items_total}, а итог чека {receipt_total}.",
        "stats_header_added_today": "📊 <b>Добавлено сегодня</b>",
        "stats_header_expense_month": "📊 <b>Текущий месяц по датам расходов</b>",
        "stats_header_expense_year": "📊 <b>Текущий год по датам расходов</b>",
        "stats_header_all": "📊 <b>Все сохраненные расходы</b>",
        "stats_empty_added_today": "Сегодня пока ничего не добавлено.",
        "stats_empty_expense_month": "В текущем месяце по датам расходов пока ничего нет.",
        "stats_empty_expense_year": "В текущем году по датам расходов пока ничего нет.",
        "stats_empty_all": "Сохраненных расходов пока нет.",
        "stats_total": "<b>Всего: {amount}</b>",
        "stats_usage": "Используй <code>/stats</code>, <code>/stats month</code>, <code>/stats year</code> или <code>/stats all</code>.",
        "family_info": "<b>Семейный бюджет</b>\nБюджет: <b>{name}</b>\nУчастников: <b>{count}</b>\n\n{members}\n\nИспользуй <code>/family_invite</code>, чтобы пригласить человека.",
        "family_invite_created": "Отправь этот код другому человеку:\n<code>{code}</code>\n\nОн сможет присоединиться командой:\n<code>/family_join {code}</code>",
        "family_join_usage": "Пришли код приглашения вот так:\n<code>/family_join ABCD2345</code>",
        "family_join_invalid": "Не нашел семейный бюджет с таким кодом приглашения.",
        "family_joined": "✅ Подключился к семейному бюджету: <b>{name}</b>.\nТеперь твои расходы, чеки, статистика и значения баланса относятся к этому общему бюджету.",
        "family_no_members": "Участников пока нет.",
        "family_role_owner": "владелец",
        "family_role_member": "участник",
        "unsupported_message": "Пришли число для текущего баланса, доход вроде <code>зарплата 3000</code>, ручной расход вроде <code>20 евро в парикмахерской</code> или фото/PDF чека.",
        "manual_income_added": "✅ Доход сохранен: <b>{amount}</b>\nОписание: {description}",
        "manual_expense_added": "✅ Расход сохранен: <b>{amount}</b>\nКатегория: <b>{category}</b>\nОписание: {description}",
        "btn_stats_today": "📊 Статистика за сегодня",
        "btn_stats_month": "📅 Месяц",
        "btn_stats_year": "Год",
        "btn_stats_all": "Всё",
        "btn_menu_balance": "💰 Баланс",
        "btn_menu_income": "Доход",
        "btn_menu_expense": "✍️ Расход",
        "btn_menu_receipt": "🧾 Чек",
        "btn_menu_stats": "📊 Статистика",
        "btn_menu_settings": "⚙️ Настройки",
        "btn_menu_language": "🌐 Язык",
        "btn_menu_family": "Семья",
        "btn_menu_back": "Назад",
        "btn_settings_start": "Изменить настройки",
        "btn_receipt_help": "🧾 Пример чека",
        "btn_expense_help": "✍️ Пример расхода",
        "btn_balance_help": "💰 Пример баланса",
        "menu_main_text": (
            "<b>Главное меню</b>\n\n"
            "Выбери, что хочешь сделать:"
        ),
        "menu_stats_text": (
            "<b>Статистика</b>\n\n"
            "Выбери период:\n"
            "• Сегодня - расходы, добавленные сегодня.\n"
            "• Месяц - текущий месяц по датам расходов.\n"
            "• Год - текущий год по датам расходов.\n"
            "• Всё - все сохраненные расходы."
        ),
        "menu_settings_text": (
            "<b>Настройки</b>\n\n"
            "Здесь можно изменить день дохода, ожидаемый ежемесячный доход и процент сбережений."
        ),
        "menu_language_text": (
            "<b>Язык</b>\n\n"
            "Выбери язык бота:"
        ),
        "help_receipt_example": (
            "Пришли чек обычным фото, файлом-картинкой или PDF.\n\n"
            "Я распознаю позиции, назначу каждой категорию, сохраню их как расходы "
            "и покажу сводку по категориям."
        ),
        "help_income_example": (
            "Сохрани доход командой:\n"
            "<code>/income 3000 зарплата</code>\n"
            "<code>/income 500 фриланс</code>\n\n"
            "Или пришли короткий текст с подсказкой, что это доход:\n"
            "<code>зарплата 3000</code>\n"
            "<code>получил 500 от клиента</code>"
        ),
        "help_expense_example": (
            "Пришли короткий расход обычным текстом:\n"
            "<code>20 евро в парикмахерской</code>\n"
            "<code>10 евро на хостинг пет-проекта</code>\n"
            "<code>5 евро на фрукты</code>\n"
            "<code>7 евро на канцелярию</code>\n\n"
            "Я сохраню его сегодняшней датой и подберу ближайшую категорию."
        ),
        "help_balance_example": (
            "Пришли баланс обычным числом:\n"
            "<code>1000</code>\n\n"
            "Или командой:\n"
            "<code>/balance 1000</code>"
        )
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
