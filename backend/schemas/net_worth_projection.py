from pydantic import BaseModel


class NetWorthProjectionPoint(
    BaseModel
):
    year: int

    investment_value: float

    real_estate_value: float
    real_estate_loan_balance: float
    real_estate_equity: float

    net_worth: float


class NetWorthProjectionResponse(
    BaseModel
):
    currency: str

    monthly_contribution: float
    annual_return_percent: float
    annual_property_growth: float

    projection_years: int

    starting_investment_value: float
    starting_real_estate_equity: float
    starting_net_worth: float

    final_investment_value: float
    final_real_estate_equity: float
    final_net_worth: float

    yearly_projection: list[
        NetWorthProjectionPoint
    ]