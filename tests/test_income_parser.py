import unittest

from src.income_parser import parse_manual_income


class TestIncomeParser(unittest.TestCase):

    def test_russian_examples_are_parsed(self):
        cases = [
            ("зарплата 3000", 3000.0, "зарплата"),
            ("получил 500 от клиента", 500.0, "клиента"),
            ("премия 100 евро", 100.0, "премия"),
        ]

        for text, amount, description in cases:
            with self.subTest(text=text):
                income = parse_manual_income(text)
                self.assertIsNotNone(income)
                self.assertEqual(income.amount, amount)
                self.assertEqual(income.description, description)

    def test_english_examples_are_parsed(self):
        cases = [
            ("salary 3000", 3000.0, "salary"),
            ("received 500 from client", 500.0, "client"),
            ("income 1200", 1200.0, None),
        ]

        for text, amount, description in cases:
            with self.subTest(text=text):
                income = parse_manual_income(text)
                self.assertIsNotNone(income)
                self.assertEqual(income.amount, amount)
                self.assertEqual(income.description, description)

    def test_plain_expense_text_is_not_income(self):
        self.assertIsNone(parse_manual_income("20 евро в парикмахерской"))

    def test_command_args_do_not_require_income_keyword(self):
        income = parse_manual_income("3000 transfer", require_keyword=False)

        self.assertIsNotNone(income)
        self.assertEqual(income.amount, 3000.0)
        self.assertEqual(income.description, "transfer")


if __name__ == '__main__':
    unittest.main()
