
import unittest
from datetime import datetime
from src.logic import calculate_budget_plan

class TestBudgetLogic(unittest.TestCase):

    def test_basic_middle_of_period(self):
        # Today: 10th. Income: 25th. Balance: 1000. Save: 10%
        # Target: 25th this month. Days: 15.
        # Save: 100. Spend: 900. Daily: 60.
        now = datetime(2023, 10, 10)
        res = calculate_budget_plan(1000, 25, 10, now)
        
        self.assertEqual(res['target_date'].day, 25)
        self.assertEqual(res['target_date'].month, 10)
        self.assertEqual(res['days_remaining'], 15)
        self.assertAlmostEqual(res['safe_to_spend_total'], 900.0)
        self.assertAlmostEqual(res['daily_budget'], 60.0)

    def test_next_month_cycle(self):
        # Today: 20th. Income: 10th. Balance: 1000. Save: 0%
        # Target: 10th NEXT month (Nov).
        # Days: (31-20) + 10 = 11 + 10 = 21 days roughly.
        now = datetime(2023, 10, 20)
        res = calculate_budget_plan(1000, 10, 0, now)
        
        self.assertEqual(res['target_date'].day, 10)
        self.assertEqual(res['target_date'].month, 11)
        # Oct has 31 days. 20th to 10th Nov is 21 days.
        self.assertEqual(res['days_remaining'], 21)
        self.assertAlmostEqual(res['daily_budget'], 1000 / 21)

    def test_same_day_cycle(self):
        # Today: 10th. Income: 10th.
        # Should push to NEXT month.
        now = datetime(2023, 10, 10)
        res = calculate_budget_plan(1000, 10, 0, now)
        
        self.assertEqual(res['target_date'].month, 11)
        self.assertEqual(res['days_remaining'], 31) # Oct has 31 days

    def test_short_month_logic(self):
        # Income day 31. Current is Feb 15th.
        # Target should be Feb 28 (or 29).
        now = datetime(2023, 2, 15) # Non leap year
        res = calculate_budget_plan(1000, 31, 0, now)
        
        self.assertEqual(res['target_date'].month, 2)
        self.assertEqual(res['target_date'].day, 28)
        self.assertEqual(res['days_remaining'], 13)

if __name__ == '__main__':
    unittest.main()
