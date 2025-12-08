
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from dotenv import load_dotenv

from db import init_db, add_or_update_user, get_user

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

class Settings(StatesGroup):
    income_day = State()
    savings_percent = State()

dp = Dispatcher()

@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    user_data = await get_user(message.from_user.id)
    if user_data:
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Welcome back. Send me your current balance to calculate your daily budget.")
    else:
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Let's set up your profile.")
        await message.answer("Please enter the day of the month you receive your income (1-31):")
        await state.set_state(Settings.income_day)

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    help_text = (
        "This bot helps you plan your daily budget.\n\n"
        "1. You set your **Income Day** and **Savings Percentage**.\n"
        "2. You send me your **Current Balance**.\n"
        "3. I calculate how much you can spend per day until your next income, saving the specified percentage.\n\n"
        "Commands:\n"
        "/start - Initialize or update settings\n"
        "/balance <amount> - Calculate budget for a specific balance (or just send the number)\n"
        "/settings - Change your settings\n"
        "/help - Show this help message"
    )
    await message.answer(help_text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("balance"))
async def command_balance_handler(message: Message, command: Command = None) -> None:
    # Check if arguments are provided
    args = message.text.split()
    if len(args) > 1:
        # User provided balance like "/balance 1000"
        try:
             balance = float(args[1])
             # Simulate a message with just the number to reuse logic, or call logic directly
             # Let's reuse the logic function but we need to pass a message object or refactor.
             # Refactoring logic out of handler is better, but for now let's just create a dummy message or modify logic.
             # Easier: Just set message.text to the balance and call calculate_budget.
             # But calculate_budget expects a message object.
             # Let's call calculate_budget with the current message, but we need to ensure message.text is just the number for it to parse?
             # No, calculate_budget parses message.text.
             # Let's refactor calculate_budget to take balance as arg or handle the parsing better.
             # Actually, simpler: just duplicate the logic small bit or make a shared function.
             pass
        except ValueError:
             await message.answer("Please provide a valid number, e.g., /balance 1000")
             return
    else:
        await message.answer("Please provide your balance, e.g., /balance 1000")
        return

    # Now run calculation
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer("Please type /start to set up your profile first.")
        return

    income_day = user_data['income_day']
    savings_percent = user_data['savings_percent']

    from logic import calculate_budget_plan
    try:
        if len(args) > 1:
             current_balance = float(args[1])
        else:
             return # Already handled above
    except ValueError:
         await message.answer("Invalid format.")
         return

    plan = calculate_budget_plan(current_balance, income_day, savings_percent)
    
    response = (
        f"💰 **Financial Plan**\n"
        f"Next Income Date: {plan['target_date'].strftime('%Y-%m-%d')}\n"
        f"Days Remaining: {plan['days_remaining']}\n"
        f"Savings ({savings_percent}%): {plan['savings_amount']:.2f}\n"
        f"Available to Spend: {plan['safe_to_spend_total']:.2f}\n"
        f"**Daily Budget: {plan['daily_budget']:.2f}**"
    )

    await message.answer(response, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("settings"))
async def command_settings_handler(message: Message, state: FSMContext) -> None:
    await message.answer("Let's update your settings.\nPlease enter the day of the month you receive your income (1-31):")
    await state.set_state(Settings.income_day)

@dp.message(Settings.income_day)
async def process_income_day(message: Message, state: FSMContext) -> None:
    try:
        day = int(message.text)
        if 1 <= day <= 31:
            await state.update_data(income_day=day)
            await message.answer("Great! Now, what percentage of your income do you NOT plan to spend? (0-100):")
            await state.set_state(Settings.savings_percent)
        else:
            await message.answer("Please enter a valid day between 1 and 31.")
    except ValueError:
        await message.answer("Please enter a number.")

@dp.message(Settings.savings_percent)
async def process_savings_percent(message: Message, state: FSMContext) -> None:
    try:
        percent = float(message.text)
        if 0 <= percent <= 100:
            data = await state.get_data()
            income_day = data['income_day']
            await add_or_update_user(message.from_user.id, income_day, percent)
            await state.clear()
            await message.answer("Settings saved! Now send me your current amount of money.")
        else:
            await message.answer("Please enter a percentage between 0 and 100.")
    except ValueError:
        await message.answer("Please enter a number.")

@dp.message()
async def calculate_budget(message: Message) -> None:
    user_data = await get_user(message.from_user.id)
    if not user_data:
        await message.answer("Please type /start to set up your profile first.")
        return

    try:
        current_balance = float(message.text)
    except ValueError:
        await message.answer("Please enter a valid number for your current balance.")
        return

    income_day = user_data['income_day']
    savings_percent = user_data['savings_percent']

    from logic import calculate_budget_plan
    
    plan = calculate_budget_plan(current_balance, income_day, savings_percent)
    
    response = (
        f"💰 **Financial Plan**\n"
        f"Next Income Date: {plan['target_date'].strftime('%Y-%m-%d')}\n"
        f"Days Remaining: {plan['days_remaining']}\n"
        f"Savings ({savings_percent}%): {plan['savings_amount']:.2f}\n"
        f"Available to Spend: {plan['safe_to_spend_total']:.2f}\n"
        f"**Daily Budget: {plan['daily_budget']:.2f}**"
    )

    await message.answer(response, parse_mode=ParseMode.MARKDOWN)

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ... existing imports ...
from db import init_db, add_or_update_user, get_user, get_all_users

async def send_daily_reminders(bot: Bot):
    users = await get_all_users()
    for user_id in users:
        try:
            # Simple localization can be added here if needed, but for now English/Default.
            # Ideally use get_msg based on user language.
             await bot.send_message(user_id, "Good morning! ☀️\nWhat is your current balance today? Send it to me to update your budget.")
        except Exception as e:
            logging.error(f"Failed to send reminder to {user_id}: {e}")

async def main() -> None:
    await init_db()
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_daily_reminders, 'cron', hour=11, minute=0, args=[bot])
    scheduler.start()

    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
