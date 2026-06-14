# Financial Planning Telegram Bot

Try it out: [@just_daily_budget_bot](https://t.me/just_daily_budget_bot)

A simple Telegram bot that helps you plan your daily spending limit.

## Features
- Set your income date and savings percentage.
- Send your current balance to get a daily budget until your next income.
- Persistent settings for each user.
- **Daily Reminders**: The bot sends you a daily reminder at 11:00 AM to update your balance.
- **Receipt Parsing**: Send a receipt photo, image file, or PDF; the bot extracts item lines and saves them by category.
- **Manual Expenses**: Send a short text like `20 euro at the barber` and the bot saves it in the closest category.

> This bot helps you stick to your financial goals and improve financial discipline.

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   - Rename `.env.example` to `.env`.
   - Add your Telegram Bot Token:
     ```
     BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
     OPENAI_API_KEY=sk-...
     OPENAI_RECEIPT_MODEL=gpt-4o-mini
     ```

3. **Run the Bot**:
   ```bash
   python src/main.py
   ```

## Usage
- `/start`: Initialize or update your settings (Income Day, Savings %).
- `/balance <amount>`: Calculate budget for a specific balance (or just send the number).
- `/settings`: Change your settings.
- `/stats`: Show expenses added today by category.
- `/stats month`: Show current-month expenses by purchase/receipt date.
- `/stats all`: Show all saved expenses by category.
- `/help`: Open the navigation menu with buttons for balance, expenses, receipts, stats, settings, and language.
- **Send a number**: Calculate your daily budget based on your saved settings.
- **Send a manual expense**: `20 euro at the barber`, `10 euro for pet-project hosting`, `5 euro for fruit`.
- **Send a receipt photo/PDF**: Parse receipt items and categorize each expense.
