from datetime import date

from pydantic import BaseModel


class RealEstateProjectionPoint(
    BaseModel
):
    year: int
    projection_date: date

    property_value: float
    loan_balance: float
    equity: float

    principal_paid: float
    interest_paid: float


class RealEstateProjectionResponse(
    BaseModel
):
    property_id: int
    property_name: str
    currency: str

    annual_property_growth: float
    annual_interest_rate: float
    monthly_payment: float

    loan_end_date: date | None
    projection_years: int

    total_principal_paid: float
    total_interest_paid: float

    points: list[
        RealEstateProjectionPoint
    ]