import unittest

from src.expense_parser import parse_manual_expense


class TestExpenseParser(unittest.TestCase):

    def test_russian_examples_are_parsed_and_categorized(self):
        cases = [
            ("20 евро в парикмахерской", 20.0, "парикмахерской", "beauty"),
            ("10 евро на хостинг пет-проекта", 10.0, "хостинг пет-проекта", "subscriptions"),
            ("5 евро на фрукты", 5.0, "фрукты", "groceries"),
            ("7 евро на канцелярию", 7.0, "канцелярию", "education"),
        ]

        for text, amount, description, category in cases:
            with self.subTest(text=text):
                expense = parse_manual_expense(text)
                self.assertIsNotNone(expense)
                self.assertEqual(expense.amount, amount)
                self.assertEqual(expense.description, description)
                self.assertEqual(expense.category, category)

    def test_amount_can_be_written_after_description(self):
        expense = parse_manual_expense("фрукты 5 евро")

        self.assertIsNotNone(expense)
        self.assertEqual(expense.amount, 5.0)
        self.assertEqual(expense.description, "фрукты")
        self.assertEqual(expense.category, "groceries")

    def test_plain_number_is_not_manual_expense(self):
        self.assertIsNone(parse_manual_expense("1000"))

    def test_expense_without_category_hint_falls_back_to_other(self):
        expense = parse_manual_expense("12 евро на странную штуку")

        self.assertIsNotNone(expense)
        self.assertEqual(expense.amount, 12.0)
        self.assertEqual(expense.description, "странную штуку")
        self.assertEqual(expense.category, "other")


if __name__ == '__main__':
    unittest.main()
