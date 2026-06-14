
import asyncio
import logging
import os
import sys
from io import BytesIO
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from db import (
    init_db,
    add_or_update_user,
    get_user,
    get_all_users,
    update_user_language,
    record_balance,
    get_balance_history,
    add_receipt_expenses,
    get_today_expense_totals,
)
from messages import get_text, get_trend_text, MESSAGES
from receipt_parser import (
    ReceiptData,
    ReceiptParserError,
    ReceiptParserUnavailable,
    category_label,
    is_supported_receipt_file,
    parse_receipt_file,
    summarize_categories,
)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

class Settings(StatesGroup):
    language_selection = State()
    income_day = State()
    monthly_income = State()
    savings_percent = State()

dp = Dispatcher()

def get_language_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=MESSAGES["en"]["btn_en"], callback_data="lang_en"),
            InlineKeyboardButton(text=MESSAGES["ru"]["btn_ru"], callback_data="lang_ru")
        ]
    ])
    return keyboard

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_data = await get_user(message.from_user.id)
    if user_data:
        lang = user_data.get('language', 'en')
        text = get_text("welcome_back", lang, name=message.from_user.full_name)
        await message.answer(text, parse_mode=ParseMode.HTML)
    else:
        # New user, ask for language
        await message.answer(
            MESSAGES["en"]["choose_language"],
            reply_markup=get_language_keyboard()
        )
        await state.set_state(Settings.language_selection)

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    user_data = await get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    help_text = get_text("help_text", lang)
    await message.answer(help_text, parse_mode=ParseMode.HTML)

@dp.message(Command("language"))
async def command_language_handler(message: Message, state: FSMContext) -> None:
    await message.answer(
        MESSAGES["en"]["choose_language"],
        reply_markup=get_language_keyboard()
    )

@dp.callback_query(F.data.startswith("lang_"))
async def language_callback_handler(callback: CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    
    # Check if user exists
    user_data = await get_user(user_id)
    
    if user_data:
        # User exists, just update language
        await update_user_language(user_id, lang_code)
        confirmation = get_text("language_set", lang_code)
        await callback.message.answer(confirmation)
        await callback.answer()
    else:
        # New user (setup flow)
        await state.update_data(language=lang_code)
        # Ask for income day
        text = get_text("welcome_new", lang_code, name=callback.from_user.full_name)
        await callback.message.answer(text, parse_mode=ParseMode.HTML)
        
        ask_text = get_text("ask_income_day", lang_code)
        await callback.message.answer(ask_text)
        
        await state.set_state(Settings.income_day)
        await callback.answer()

@dp.message(Command("balance"))
async def command_balance_handler(message: Message, command: Command = None) -> None:
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer(get_text("start_first", "en"))
        return

    lang = user_data.get('language', 'en')

    args = message.text.split()
    if len(args) > 1:
        try:
             float(args[1])
        except ValueError:
             await message.answer(get_text("provide_balance_args", lang))
             return
    else:
        await message.answer(get_text("provide_balance", lang))
        return

    current_balance = float(args[1])
    await run_calculation(message, user_data, current_balance, lang)

@dp.message(Command("settings"))
async def command_settings_handler(message: Message, state: FSMContext) -> None:
    user_data = await get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    await message.answer(get_text("update_settings", lang))
    await state.set_state(Settings.income_day)
    await state.update_data(language=lang)

@dp.message(Settings.income_day)
async def process_income_day(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'en')
    if 'language' not in data:
        user_data = await get_user(message.from_user.id)
        lang = user_data.get('language', 'en') if user_data else 'en'
        await state.update_data(language=lang)

    try:
        day = int(message.text)
        if 1 <= day <= 31:
            await state.update_data(income_day=day)
            # Next step: Monthly Income
            await message.answer(get_text("ask_monthly_income", lang))
            await state.set_state(Settings.monthly_income)
        else:
            await message.answer(get_text("invalid_day", lang))
    except ValueError:
        await message.answer(get_text("not_number", lang))

@dp.message(Settings.monthly_income)
async def process_monthly_income(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'en')
    
    try:
        income = float(message.text)
        if income > 0:
             await state.update_data(monthly_income=income)
             await message.answer(get_text("ask_savings", lang))
             await state.set_state(Settings.savings_percent)
        else:
             await message.answer(get_text("invalid_income", lang))
    except ValueError:
        await message.answer(get_text("not_number", lang))

@dp.message(Settings.savings_percent)
async def process_savings_percent(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'en')
    
    try:
        percent = float(message.text)
        if 0 <= percent <= 100:
            income_day = data['income_day']
            monthly_income = data['monthly_income']
            
            # Save to DB
            await add_or_update_user(message.from_user.id, income_day, percent, lang, monthly_income)
            await state.clear()
            await message.answer(get_text("settings_saved", lang))
        else:
            await message.answer(get_text("invalid_percent", lang))
    except ValueError:
        await message.answer(get_text("not_number", lang))

@dp.message(Command("stats"))
async def command_stats_handler(message: Message) -> None:
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer(get_text("start_first", "en"))
        return

    lang = user_data.get('language', 'en')
    totals = await get_today_expense_totals(message.from_user.id)
    if not totals:
        await message.answer(get_text("stats_empty", lang))
        return

    lines = [get_text("stats_header", lang)]
    grand_total = 0.0
    for row in totals:
        grand_total += row["amount"]
        lines.append(
            f"• {html.quote(category_label(row['category'], lang))}: "
            f"{row['amount']:.2f} ({row['count']})"
        )
    lines.append(get_text("stats_total", lang, amount=f"{grand_total:.2f}"))
    await message.answer("\n".join(lines), parse_mode=ParseMode.HTML)

@dp.message(F.photo)
async def receipt_photo_handler(message: Message) -> None:
    await handle_receipt_upload(message, source_type="photo")

@dp.message(F.document)
async def receipt_document_handler(message: Message) -> None:
    document = message.document
    mime_type = (document.mime_type or "").lower()
    filename = document.file_name or ""
    if not is_supported_receipt_file(mime_type, filename):
        user_data = await get_user(message.from_user.id)
        lang = user_data.get('language', 'en') if user_data else 'en'
        await message.answer(get_text("receipt_unsupported_file", lang))
        return

    await handle_receipt_upload(message, source_type="document")

async def handle_receipt_upload(message: Message, source_type: str) -> None:
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer(get_text("start_first", "en"))
        return

    lang = user_data.get('language', 'en')
    await message.answer(get_text("receipt_processing", lang))

    try:
        file_bytes, mime_type, filename = await download_receipt_file(message, source_type)
        receipt = await parse_receipt_file(file_bytes, mime_type, filename)
        await save_receipt(message.from_user.id, receipt, source_type)
    except ReceiptParserUnavailable:
        await message.answer(get_text("receipt_parser_unavailable", lang))
        return
    except ReceiptParserError as exc:
        logging.warning("Failed to parse receipt for user %s: %s", message.from_user.id, exc)
        await message.answer(get_text("receipt_parse_failed", lang))
        return
    except Exception:
        logging.exception("Unexpected receipt processing error for user %s", message.from_user.id)
        await message.answer(get_text("receipt_parse_failed", lang))
        return

    await message.answer(format_receipt_summary(receipt, lang), parse_mode=ParseMode.HTML)

async def download_receipt_file(message: Message, source_type: str) -> tuple[bytes, str, str | None]:
    buffer = BytesIO()
    if source_type == "photo":
        photo = message.photo[-1]
        await message.bot.download(photo, destination=buffer)
        return buffer.getvalue(), "image/jpeg", None

    document = message.document
    await message.bot.download(document, destination=buffer)
    return buffer.getvalue(), document.mime_type or "application/octet-stream", document.file_name

async def save_receipt(user_id: int, receipt: ReceiptData, source_type: str) -> int:
    items = [
        {
            "amount": item.amount,
            "description": item.name,
            "category": item.category,
        }
        for item in receipt.items
    ]
    return await add_receipt_expenses(
        user_id=user_id,
        merchant=receipt.merchant,
        purchased_at=receipt.purchased_at,
        total=receipt.total,
        currency=receipt.currency,
        items=items,
        source_type=source_type,
    )

def format_receipt_summary(receipt: ReceiptData, lang: str) -> str:
    merchant = html.quote(receipt.merchant or get_text("receipt_unknown_store", lang))
    total_value = receipt.total if receipt.total is not None else receipt.items_total
    lines = [
        get_text(
            "receipt_saved",
            lang,
            merchant=merchant,
            total=f"{total_value:.2f}",
            currency=html.quote(receipt.currency),
            count=len(receipt.items),
        ),
        "",
        get_text("receipt_categories_header", lang),
    ]

    for category_id, amount, count in summarize_categories(receipt.items):
        lines.append(f"• {html.quote(category_label(category_id, lang))}: {amount:.2f} ({count})")

    shown_items = receipt.items[:8]
    if shown_items:
        lines.append("")
        lines.append(get_text("receipt_items_header", lang))
        for item in shown_items:
            lines.append(
                f"• {html.quote(item.name)} - {item.amount:.2f} "
                f"-> {html.quote(category_label(item.category, lang))}"
            )

    hidden_count = len(receipt.items) - len(shown_items)
    if hidden_count > 0:
        lines.append(get_text("receipt_more_items", lang, count=hidden_count))

    if receipt.total is not None and abs(receipt.items_total - receipt.total) > 0.05:
        lines.append("")
        lines.append(get_text(
            "receipt_total_mismatch",
            lang,
            items_total=f"{receipt.items_total:.2f}",
            receipt_total=f"{receipt.total:.2f}",
        ))

    return "\n".join(lines)

@dp.message()
async def calculate_budget_message(message: Message) -> None:
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer(get_text("start_first", "en"))
        return

    lang = user_data.get('language', 'en')

    if not message.text:
        await message.answer(get_text("unsupported_message", lang))
        return
    if message.text.startswith('/'): return

    try:
        current_balance = float(message.text)
    except ValueError:
        await message.answer(get_text("invalid_balance", lang))
        return

    await run_calculation(message, user_data, current_balance, lang, record_history=True)

async def run_calculation(message: Message, user_data: dict, current_balance: float, lang: str, record_history: bool = False):
    income_day = user_data['income_day']
    savings_percent = user_data['savings_percent']
    monthly_income = user_data.get('monthly_income', 0)

    # Check if monthly_income is set properly (validation for old users)
    if not monthly_income or monthly_income <= 0:
        await message.answer(get_text("settings_incomplete", lang))
        # Start settings flow? Or just prompt user to do it.
        # "Settings incomplete" message handles it.
        return

    from logic import calculate_budget_plan, estimate_runway

    now = datetime.now()
    plan = calculate_budget_plan(current_balance, income_day, savings_percent, monthly_income, now=now)

    # Persist the reading (only on the "this is my real balance" path) and
    # forecast how long the money lasts at the actual spending pace.
    if record_history:
        await record_balance(message.from_user.id, current_balance, now)
    history = await get_balance_history(message.from_user.id)
    runway = estimate_runway(history, current_balance, now=now)

    response = get_text("financial_plan", lang,
        next_income=plan['target_date'].strftime('%Y-%m-%d'),
        days_remaining=plan['days_remaining'],
        savings_percent=savings_percent,
        monthly_income=f"{monthly_income:.2f}",
        savings_amount=f"{plan['savings_amount']:.2f}",
        safe_to_spend=f"{plan['safe_to_spend_total']:.2f}",
        daily_budget=f"{plan['daily_budget']:.2f}"
    )

    trend = get_trend_text(runway, plan['days_remaining'], lang)
    if trend:
        response = f"{response}\n\n{trend}"

    await message.answer(response, parse_mode=ParseMode.HTML)

# Scheduler
async def send_daily_reminders(bot: Bot):
    users = await get_all_users()
    for user_id in users:
        try:
            user_data = await get_user(user_id)
            lang = user_data.get('language', 'en') if user_data else 'en'
            await bot.send_message(user_id, get_text("reminder", lang))
        except Exception as e:
            logging.error(f"Failed to send reminder to {user_id}: {e}")

async def main() -> None:
    await init_db()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_reminders, 'cron', hour=11, minute=0, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
