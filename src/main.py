
import asyncio
import logging
import os
import sys
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

from db import init_db, add_or_update_user, get_user, get_all_users, update_user_language, add_expense, get_today_expenses
from messages import get_text, MESSAGES

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

@dp.message()
async def calculate_budget_message(message: Message) -> None:
    if message.text.startswith('/'): return
    
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer(get_text("start_first", "en"))
        return

    lang = user_data.get('language', 'en')

    try:
        current_balance = float(message.text)
    except ValueError:
        await message.answer(get_text("invalid_balance", lang))
        return

    await run_calculation(message, user_data, current_balance, lang)

async def run_calculation(message: Message, user_data: dict, current_balance: float, lang: str):
    income_day = user_data['income_day']
    savings_percent = user_data['savings_percent']
    monthly_income = user_data.get('monthly_income', 0)
    
    # Check if monthly_income is set properly (validation for old users)
    if not monthly_income or monthly_income <= 0:
        await message.answer(get_text("settings_incomplete", lang))
        # Start settings flow? Or just prompt user to do it.
        # "Settings incomplete" message handles it.
        return

    from logic import calculate_budget_plan
    
    plan = calculate_budget_plan(current_balance, income_day, savings_percent, monthly_income)
    
    response = get_text("financial_plan", lang,
        next_income=plan['target_date'].strftime('%Y-%m-%d'),
        days_remaining=plan['days_remaining'],
        savings_percent=savings_percent,
        monthly_income=f"{monthly_income:.2f}",
        savings_amount=f"{plan['savings_amount']:.2f}",
        safe_to_spend=f"{plan['safe_to_spend_total']:.2f}",
        daily_budget=f"{plan['daily_budget']:.2f}"
    )

    await message.answer(response, parse_mode=ParseMode.HTML)

@dp.message(Command("expense"))
async def command_expense_handler(message: Message) -> None:
    user_data = await get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    args = message.text.split(maxsplit=2)
    # /expense 100 Description
    if len(args) < 2:
        await message.answer(get_text("expense_format_error", lang))
        return
        
    try:
        amount = float(args[1])
        description = args[2] if len(args) > 2 else ""
        
        await add_expense(message.from_user.id, amount, description)
        await message.answer(get_text("expense_added", lang, amount=amount, description=description))
        
    except ValueError:
        await message.answer(get_text("not_number", lang))

@dp.message(Command("stats"))
async def command_stats_handler(message: Message) -> None:
    user_data = await get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    total = await get_today_expenses(message.from_user.id)
    
    await message.answer(get_text("stats_today", lang, amount=f"{total:.2f}"), parse_mode=ParseMode.HTML)

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
