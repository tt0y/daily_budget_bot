
import unittest
from datetime import datetime
from src.logic import calculate_budget_plan, estimate_runway

class TestBudgetLogic(unittest.TestCase):

    def test_basic_middle_of_period(self):
        # Today: 10th. Income: 25th. Balance: 1000. Income: 1000, Save: 10%.
        # Target: 25th this month. Days: 15.
        # Save: 100. Spend: 900. Daily: 60.
        now = datetime(2023, 10, 10)
        res = calculate_budget_plan(1000, 25, 10, monthly_income=1000, now=now)

        self.assertEqual(res['target_date'].day, 25)
        self.assertEqual(res['target_date'].month, 10)
        self.assertEqual(res['days_remaining'], 15)
        self.assertAlmostEqual(res['savings_amount'], 100.0)
        self.assertAlmostEqual(res['safe_to_spend_total'], 900.0)
        self.assertAlmostEqual(res['daily_budget'], 60.0)

    def test_next_month_cycle(self):
        # Today: 20th. Income: 10th. Balance: 1000. Save: 0%.
        # Target: 10th NEXT month (Nov).
        # Days: (31-20) + 10 = 11 + 10 = 21 days roughly.
        now = datetime(2023, 10, 20)
        res = calculate_budget_plan(1000, 10, 0, monthly_income=1000, now=now)

        self.assertEqual(res['target_date'].day, 10)
        self.assertEqual(res['target_date'].month, 11)
        # Oct has 31 days. 20th to 10th Nov is 21 days.
        self.assertEqual(res['days_remaining'], 21)
        self.assertAlmostEqual(res['daily_budget'], 1000 / 21)

    def test_same_day_cycle(self):
        # Today: 10th. Income: 10th.
        # Should push to NEXT month.
        now = datetime(2023, 10, 10)
        res = calculate_budget_plan(1000, 10, 0, monthly_income=1000, now=now)

        self.assertEqual(res['target_date'].month, 11)
        self.assertEqual(res['days_remaining'], 31)  # Oct has 31 days

    def test_short_month_logic(self):
        # Income day 31. Current is Feb 15th.
        # Target should be Feb 28 (or 29).
        now = datetime(2023, 2, 15)  # Non leap year
        res = calculate_budget_plan(1000, 31, 0, monthly_income=1000, now=now)

        self.assertEqual(res['target_date'].month, 2)
        self.assertEqual(res['target_date'].day, 28)
        self.assertEqual(res['days_remaining'], 13)


class TestRunway(unittest.TestCase):

    def test_steady_spending(self):
        # Spent 200 over 2 days -> 100/day. Balance 800 -> 8 days left.
        now = datetime(2023, 10, 10)
        history = [
            (datetime(2023, 10, 1), 1000),
            (datetime(2023, 10, 2), 900),
            (datetime(2023, 10, 3), 800),
        ]
        res = estimate_runway(history, 800, now=now)
        self.assertTrue(res['has_estimate'])
        self.assertEqual(res['reason'], 'ok')
        self.assertAlmostEqual(res['daily_spend'], 100.0)
        self.assertAlmostEqual(res['days_left'], 8.0)

    def test_income_jump_is_ignored(self):
        # Two declining intervals of 100 over 1 day each; the income jump between
        # them must be skipped, not counted as negative spending.
        now = datetime(2023, 10, 10)
        history = [
            (datetime(2023, 10, 1), 500),
            (datetime(2023, 10, 2), 400),   # spent 100 over 1 day
            (datetime(2023, 10, 3), 2000),  # income jump -> skipped
            (datetime(2023, 10, 4), 1900),  # spent 100 over 1 day
        ]
        res = estimate_runway(history, 1900, now=now)
        self.assertAlmostEqual(res['daily_spend'], 100.0)
        self.assertAlmostEqual(res['days_left'], 19.0)

    def test_fractional_days(self):
        # 300 spent over exactly 2 days -> 150/day.
        now = datetime(2023, 10, 10, 12, 0, 0)
        history = [
            (datetime(2023, 10, 8, 12, 0, 0), 600),
            (datetime(2023, 10, 10, 12, 0, 0), 300),
        ]
        res = estimate_runway(history, 300, now=now)
        self.assertAlmostEqual(res['daily_spend'], 150.0)
        self.assertAlmostEqual(res['days_left'], 2.0)

    def test_window_excludes_old_points(self):
        # Old August points fall outside the 30-day window and must not skew it.
        now = datetime(2023, 10, 31)
        history = [
            (datetime(2023, 8, 1), 5000),
            (datetime(2023, 8, 2), 4000),
            (datetime(2023, 10, 20), 1100),
            (datetime(2023, 10, 30), 100),  # 1000 over 10 days -> 100/day
        ]
        res = estimate_runway(history, 100, now=now, window_days=30)
        self.assertAlmostEqual(res['daily_spend'], 100.0)

    def test_empty_history(self):
        now = datetime(2023, 10, 10)
        res = estimate_runway([], 500, now=now)
        self.assertFalse(res['has_estimate'])
        self.assertEqual(res['reason'], 'insufficient_history')

    def test_single_point(self):
        now = datetime(2023, 10, 10)
        res = estimate_runway([(datetime(2023, 10, 9), 500)], 500, now=now)
        self.assertFalse(res['has_estimate'])
        self.assertEqual(res['reason'], 'insufficient_history')

    def test_only_increases(self):
        # Balance only grows -> every interval is income -> nothing usable.
        now = datetime(2023, 10, 10)
        history = [
            (datetime(2023, 10, 1), 100),
            (datetime(2023, 10, 2), 200),
            (datetime(2023, 10, 3), 300),
        ]
        res = estimate_runway(history, 300, now=now)
        self.assertFalse(res['has_estimate'])
        self.assertEqual(res['reason'], 'insufficient_history')

    def test_flat_balance_no_spending(self):
        now = datetime(2023, 10, 10)
        history = [
            (datetime(2023, 10, 1), 500),
            (datetime(2023, 10, 2), 500),
            (datetime(2023, 10, 3), 500),
        ]
        res = estimate_runway(history, 500, now=now)
        self.assertFalse(res['has_estimate'])
        self.assertEqual(res['reason'], 'no_spending')

    def test_depleted_balance(self):
        now = datetime(2023, 10, 10)
        history = [
            (datetime(2023, 10, 1), 100),
            (datetime(2023, 10, 2), 50),
        ]
        res = estimate_runway(history, 0, now=now)
        self.assertTrue(res['has_estimate'])
        self.assertEqual(res['reason'], 'depleted')
        self.assertEqual(res['days_left'], 0.0)


if __name__ == '__main__':
    unittest.main()
