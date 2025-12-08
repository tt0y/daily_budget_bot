
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

def calculate_budget_plan(current_balance: float, income_day: int, savings_percent: float, now: datetime = None):
    if now is None:
        now = datetime.now()
    
    # Calculate next income date
    if now.day < income_day:
        # Income is this month
        try:
             target_date = now.replace(day=income_day)
        except ValueError:
             # Fallback if today involves a day that doesn't exist in target month (unlikely here as it's same month)
             # But if income_day is 31 and current month has 30?
             # Actually if now.day < income_day, then income_day must be valid for this month?
             # Not necessarily if income_day is set to 31 generally, and we are in June (30 days).
             # If user set 31, and we are in June, target should probably be June 30?
             last_day_current = calendar.monthrange(now.year, now.month)[1]
             target_date = now.replace(day=min(income_day, last_day_current))
    else:
        # Income is next month
        next_month = now + relativedelta(months=1)
        last_day_next = calendar.monthrange(next_month.year, next_month.month)[1]
        target_date = next_month.replace(day=min(income_day, last_day_next))

    days_remaining = (target_date - now).days
    
    # Guard against 0 days if running exactly on the day (should ideally imply full cycle, but let's keep it simple)
    # If days_remaining is 0, it means it's the payday.
    # Usually you plan for the NEXT payday.
    # But if logic says: today >= income_day -> next month.
    # So if today is 25th and income is 25th -> next month 25th. Days remaining ~30.
    # So days_remaining = 0 is only possible if target calculation yielded today.
    # Which shouldn't happen with the >= logic.
    
    safe_to_spend_total = current_balance * (1 - savings_percent / 100)
    daily_budget = safe_to_spend_total / days_remaining if days_remaining > 0 else safe_to_spend_total

    return {
        "target_date": target_date,
        "days_remaining": days_remaining,
        "savings_amount": current_balance * (savings_percent / 100),
        "safe_to_spend_total": safe_to_spend_total,
        "daily_budget": daily_budget
    }
