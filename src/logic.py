
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar

def calculate_budget_plan(current_balance: float, income_day: int, savings_percent: float, monthly_income: float = 0, now: datetime = None):
    if now is None:
        now = datetime.now()
    
    # Calculate next income date
    if now.day < income_day:
        # Income is this month
        try:
             target_date = now.replace(day=income_day)
        except ValueError:
             last_day_current = calendar.monthrange(now.year, now.month)[1]
             target_date = now.replace(day=min(income_day, last_day_current))
    else:
        # Income is next month
        next_month = now + relativedelta(months=1)
        last_day_next = calendar.monthrange(next_month.year, next_month.month)[1]
        target_date = next_month.replace(day=min(income_day, last_day_next))

    days_remaining = (target_date - now).days
    
    # Calculate fixed savings amount
    # If monthly_income is 0 (legacy or not set), we might fallback to old logic?
    # User requested FIX, implying old logic was wrong.
    # But if monthly_income is 0, we can't calculate fixed amount meaningfully other than 0.
    # Let's assume user set it. If 0, savings amount is 0.
    
    savings_amount = monthly_income * (savings_percent / 100)
    
    # Safe to spend is current balance minus savings we MUST keep intact.
    # Wait, check logic: 
    # "need to subtract a fixed amount"
    
    safe_to_spend_total = current_balance - savings_amount
    
    # If negative, it means we dipped into savings
    daily_budget = safe_to_spend_total / days_remaining if days_remaining > 0 else safe_to_spend_total

    return {
        "target_date": target_date,
        "days_remaining": days_remaining,
        "savings_amount": savings_amount,
        "safe_to_spend_total": safe_to_spend_total,
        "daily_budget": daily_budget
    }
