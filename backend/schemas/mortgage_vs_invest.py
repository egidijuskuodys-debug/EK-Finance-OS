from datetime import date

from pydantic import (
    BaseModel,
    Field,
)


class MortgageVsInvestRequest(
    BaseModel
):
    monthly_extra_amount: float = Field(
        default=400.0,
        gt=0,
        le=100000,
    )

    hybrid_mortgage_percentage: float = Field(
        default=50.0,
        ge=0,
        le=100,
    )

    annual_investment_returns: list[
        float
    ] = Field(
        default_factory=lambda: [
            5.0,
            7.0,
            9.0,
        ],
        min_length=1,
        max_length=10,
    )


class MortgageBaseline(
    BaseModel
):
    loan_balance: float
    annual_interest_rate: float
    monthly_payment: float
    remaining_months: int
    loan_end_date: date | None

    total_interest: float
    total_paid: float


class MortgageStrategyOutcome(
    BaseModel
):
    strategy: str
    description: str

    mortgage_monthly_amount: float
    investment_monthly_amount: float

    payoff_months: int
    payoff_date: date

    interest_paid: float
    interest_saved: float

    investment_value_at_horizon: float
    advantage_vs_invest_only: float


class MortgageReturnComparison(
    BaseModel
):
    annual_investment_return: float

    invest_only: MortgageStrategyOutcome
    repay_first: MortgageStrategyOutcome
    hybrid: MortgageStrategyOutcome

    winner: str
    winner_value: float
    difference_to_second: float


class MortgageVsInvestResponse(
    BaseModel
):
    property_id: int
    property_name: str
    currency: str

    monthly_extra_amount: float
    hybrid_mortgage_percentage: float

    calculation_date: date
    comparison_end_date: date
    break_even_annual_return: float | None

    baseline: MortgageBaseline

    comparisons: list[
        MortgageReturnComparison
    ]

    assumptions: list[str]
