import unittest
from unittest.mock import MagicMock, patch
from datetime import date
from aws_cost_summary import display_cost_changes
import io
import sys

print(sys.path)


class TestCostMonitor(unittest.TestCase):

    def setUp(self):
        # Mock accounts dictionary
        self.accounts = {"123456789012": "Account1", "987654321098": "Account2"}

        # Mock account costs data
        self.account_costs = {
            "123456789012": {
                "last_month": 500.0,
                "two_months_ago": 450.0,
                "three_months_ago": 430.0,
                "four_months_ago": 410.0,
                "five_months_ago": 400.0,
            },
            "987654321098": {
                "last_month": 1500.0,
                "two_months_ago": 1400.0,
                "three_months_ago": 1300.0,
                "four_months_ago": 1200.0,
                "five_months_ago": 1100.0,
            },
        }

        # Mock date ranges
        self.last_month_start = date(2023, 8, 1)
        self.two_months_ago_start = date(2023, 7, 1)
        self.three_months_ago_start = date(2023, 6, 1)
        self.four_months_ago_start = date(2023, 5, 1)
        self.five_months_ago_start = date(2023, 4, 1)

        # Mock boto3 client
        self.mock_client = MagicMock()

    def test_display_cost_changes(self):
        # Capture the printed output
        with patch("sys.stdout", new=io.StringIO()) as fake_out:
            display_cost_changes(
                self.mock_client,
                self.accounts,
                self.account_costs,
                self.last_month_start,
                self.two_months_ago_start,
                self.three_months_ago_start,
                self.four_months_ago_start,
                self.five_months_ago_start,
            )

            output = fake_out.getvalue()
            sys.__stdout__.write(output + "\n")  # Print for visual inspection

            # Assert account name, cost values and date in output.
            self.assertIn("Account1", output)
            self.assertIn("500.00", output)
            self.assertIn("1,500.00", output)
            self.assertIn("Aug 2023", output)


if __name__ == "__main__":
    unittest.main()
