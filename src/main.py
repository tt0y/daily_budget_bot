
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

from db import init_db, add_or_update_user, get_user, get_all_users, update_user_language
from messages import get_text, MESSAGES

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

class Settings(StatesGroup):
    language_selection = State()
    income_day = State()
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
    # Allow changing language explicitly
    await message.answer(
        MESSAGES["en"]["choose_language"],
        reply_markup=get_language_keyboard()
    )
    # We don't necessarily need to set state if we handle it via callback generically,
    # but setting state helps if we want to enforce flow. 
    # However, for an existing user, we just want to update language.
    # Let's handle callback globally or specific state? 
    # Let's use a global callback handler for language switching to keep it simple.
    

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
        # Try to guess lang or default en
        await message.answer(get_text("start_first", "en"))
        return

    lang = user_data.get('language', 'en')

    args = message.text.split()
    if len(args) > 1:
        try:
             # Just validating number here
             float(args[1])
        except ValueError:
             await message.answer(get_text("provide_balance_args", lang))
             return
    else:
        await message.answer(get_text("provide_balance", lang))
        return

    # Now run calculation logic (reusing calculate_budget function logic)
    # To keep it DRY, I'll invoke calculate_budget or extract logic.
    # For now, let's just create a dummy message with the text or handle it here.
    # Logic extraction is cleaner.
    
    current_balance = float(args[1])
    await run_calculation(message, user_data, current_balance, lang)

@dp.message(Command("settings"))
async def command_settings_handler(message: Message, state: FSMContext) -> None:
    user_data = await get_user(message.from_user.id)
    lang = user_data.get('language', 'en') if user_data else 'en'
    
    await message.answer(get_text("update_settings", lang))
    await state.set_state(Settings.income_day)
    # We should preserve language in state if needed, but we can look it up later.
    # Actually, process_income_day needs to know language to reply. 
    # State data is cleared on retrieval? No.
    # Let's put language in state if it's not there? 
    # Better: fetch user language in the handler.
    await state.update_data(language=lang)


@dp.message(Settings.income_day)
async def process_income_day(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get('language', 'en')
    # If language not in state (e.g. restart), try fetch from DB or default
    if 'language' not in data:
        user_data = await get_user(message.from_user.id)
        lang = user_data.get('language', 'en') if user_data else 'en'
        await state.update_data(language=lang)

    try:
        day = int(message.text)
        if 1 <= day <= 31:
            await state.update_data(income_day=day)
            await message.answer(get_text("ask_savings", lang))
            await state.set_state(Settings.savings_percent)
        else:
            await message.answer(get_text("invalid_day", lang))
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
            # Save to DB
            await add_or_update_user(message.from_user.id, income_day, percent, lang)
            await state.clear()
            await message.answer(get_text("settings_saved", lang))
        else:
            await message.answer(get_text("invalid_percent", lang))
    except ValueError:
        await message.answer(get_text("not_number", lang))

@dp.message()
async def calculate_budget_message(message: Message) -> None:
    if message.text.startswith('/'): return # Ignore other commands
    
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

    from logic import calculate_budget_plan
    
    plan = calculate_budget_plan(current_balance, income_day, savings_percent)
    
    response = get_text("financial_plan", lang,
        next_income=plan['target_date'].strftime('%Y-%m-%d'),
        days_remaining=plan['days_remaining'],
        savings_percent=savings_percent,
        savings_amount=f"{plan['savings_amount']:.2f}",
        safe_to_spend=f"{plan['safe_to_spend_total']:.2f}",
        daily_budget=f"{plan['daily_budget']:.2f}"
    )

    await message.answer(response, parse_mode=ParseMode.HTML)

# Scheduler
async def send_daily_reminders(bot: Bot):
    users = await get_all_users() # This returns IDs
    # To localize reminders, we need to fetch user language.
    # get_all_users only returns IDs.
    # optimization: fetch language with IDs? 
    # For now, let's iterate and fetch user. A bit slow but ok for small bot.
    # Alternatively update get_all_users to return dicts.
    
    # Let's do it inside loop for now.
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
