from pydantic import BaseModel


class FinancialIndependencePoint(
    BaseModel
):
    year: int

    investment_value: float
    real_estate_equity: float
    net_worth: float

    investment_monthly_passive_income: float
    rental_monthly_cash_flow: float
    monthly_passive_income: float

    target_reached: bool


class FinancialIndependenceResponse(
    BaseModel
):
    currency: str

    monthly_income_target: float
    annual_income_target: float
    withdrawal_rate_percent: float

    investment_income_target: float
    required_capital: float

    current_fi_capital: float
    current_net_worth: float
    current_real_estate_equity: float

    investment_monthly_passive_income: float
    rental_monthly_cash_flow: float
    current_monthly_passive_income: float

    remaining_gap: float
    progress_percent: float

    years_to_goal: int | None
    current_age: int
    projected_age_at_goal: int | None

    monthly_contribution: float
    annual_return_percent: float
    annual_property_growth: float

    yearly_projection: list[
        FinancialIndependencePoint
    ]