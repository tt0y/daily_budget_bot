# Financial Planning Telegram Bot

Try it out: [@just_daily_budget_bot](https://t.me/just_daily_budget_bot)

A simple Telegram bot that helps you plan your daily spending limit.

## Features
- Set your income date and savings percentage.
- Send your current balance to get a daily budget until your next income.
- Persistent settings for each user.
- **Daily Reminders**: The bot sends you a daily reminder at 11:00 AM to update your balance.

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
     ```

3. **Run the Bot**:
   ```bash
   python src/main.py
   ```

## Usage
- `/start`: Initialize or update your settings (Income Day, Savings %).
- `/balance <amount>`: Calculate budget for a specific balance (or just send the number).
- `/settings`: Change your settings.
- `/help`: Get help.
- **Send a number**: Calculate your daily budget based on your saved settings.
