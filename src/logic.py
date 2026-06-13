
from datetime import datetime, timedelta
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


def estimate_runway(history, current_balance: float, now: datetime = None, window_days: int = 30):
    """Estimate how long the money will last at the recent spending pace.

    `history` is a list of (timestamp: datetime, balance: float) points. It is
    expected to be the user's recorded balance readings over time. We derive the
    daily burn rate from the differences between consecutive readings:
      - declining/flat intervals are real spending and are averaged together;
      - rising intervals (income or a top-up) are skipped, so they don't distort
        the burn rate.
    `days_left = current_balance / daily_spend`.

    Returns a dict: {has_estimate, daily_spend, days_left, reason}. Possible
    reasons: "ok", "depleted", "no_spending", "insufficient_history".
    """
    if now is None:
        now = datetime.now()

    points = sorted((p for p in history if p[0] is not None), key=lambda p: p[0])

    # Prefer recent behavior, but fall back to the full history if the window
    # leaves us with too few points to compute a difference.
    if len(points) >= 2:
        cutoff = now - timedelta(days=window_days)
        windowed = [p for p in points if p[0] >= cutoff]
        if len(windowed) >= 2:
            points = windowed

    if len(points) < 2:
        return {"has_estimate": False, "daily_spend": None, "days_left": None, "reason": "insufficient_history"}

    spent = 0.0
    span_days = 0.0
    for (t_prev, bal_prev), (t_curr, bal_curr) in zip(points, points[1:]):
        dt_days = (t_curr - t_prev).total_seconds() / 86400.0
        if dt_days <= 0:
            continue
        delta = bal_prev - bal_curr  # positive => money was spent
        if delta < 0:
            # Balance went up: income / top-up, not spending. Skip the interval.
            continue
        spent += delta
        span_days += dt_days

    if span_days <= 0:
        # No usable spending intervals (single point, or only income jumps).
        return {"has_estimate": False, "daily_spend": None, "days_left": None, "reason": "insufficient_history"}

    daily_spend = spent / span_days
    if daily_spend <= 0:
        # Balance never declined over the observed period.
        return {"has_estimate": False, "daily_spend": 0.0, "days_left": None, "reason": "no_spending"}

    if current_balance <= 0:
        return {"has_estimate": True, "daily_spend": daily_spend, "days_left": 0.0, "reason": "depleted"}

    days_left = current_balance / daily_spend
    return {"has_estimate": True, "daily_spend": daily_spend, "days_left": days_left, "reason": "ok"}
