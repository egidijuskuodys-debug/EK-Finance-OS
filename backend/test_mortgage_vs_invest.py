import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from schemas.mortgage_vs_invest import MortgageVsInvestRequest
from services.mortgage_vs_invest_service import add_months, get_mortgage_vs_invest


class MortgageVsInvestTests(unittest.TestCase):
    def compare(self, monthly_payment, interest_rate=0, loan_balance=1200):
        property_record = SimpleNamespace(
            id=1,
            name="Apartment",
            currency="EUR",
            loan_balance=loan_balance,
            interest_rate=interest_rate,
            monthly_payment=monthly_payment,
            loan_end_date=add_months(date.today(), 12),
        )
        with patch(
            "services.mortgage_vs_invest_service."
            "real_estate_repository.get_property_by_id",
            return_value=property_record,
        ):
            return get_mortgage_vs_invest(
                db=None,
                property_id=1,
                request=MortgageVsInvestRequest(monthly_extra_amount=100),
            )

    def test_rejects_hidden_final_balloon_payment(self):
        with self.assertRaisesRegex(ValueError, "does not repay"):
            self.compare(monthly_payment=50)

    def test_accepts_affordable_payment(self):
        comparison = self.compare(monthly_payment=100)
        self.assertEqual(comparison["baseline"]["total_paid"], 1200)
        self.assertEqual(
            comparison["comparisons"][0]["invest_only"]["interest_paid"],
            0,
        )

    def test_break_even_matches_mortgage_rate_without_fees(self):
        comparison = self.compare(monthly_payment=110, interest_rate=4)
        self.assertAlmostEqual(
            comparison["break_even_annual_return"],
            4,
            delta=0.05,
        )

    def test_no_break_even_without_outstanding_loan(self):
        comparison = self.compare(monthly_payment=0, loan_balance=0)
        self.assertIsNone(comparison["break_even_annual_return"])


if __name__ == "__main__":
    unittest.main()
