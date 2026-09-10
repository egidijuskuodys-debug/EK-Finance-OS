from datetime import date

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class RealEstateBase(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )

    address: str | None = Field(
        default=None,
        max_length=250,
    )

    property_type: str = Field(
        default="Apartment",
        min_length=1,
        max_length=50,
    )

    purchase_price: float = Field(
        ge=0,
    )

    current_value: float = Field(
        ge=0,
    )

    down_payment: float = Field(
        default=0.0,
        ge=0,
    )

    loan_original_amount: float = Field(
        default=0.0,
        ge=0,
    )

    loan_balance: float = Field(
        default=0.0,
        ge=0,
    )

    interest_rate: float | None = Field(
        default=None,
        ge=0,
    )

    monthly_payment: float = Field(
        default=0.0,
        ge=0,
    )

    monthly_rent: float = Field(
        default=0.0,
        ge=0,
    )

    monthly_expenses: float = Field(
        default=0.0,
        ge=0,
    )

    currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=10,
    )

    purchase_date: date | None = None

    loan_end_date: date | None = None


class RealEstateCreate(
    RealEstateBase
):
    pass


class RealEstateUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    address: str | None = Field(
        default=None,
        max_length=250,
    )

    property_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    purchase_price: float | None = Field(
        default=None,
        ge=0,
    )

    current_value: float | None = Field(
        default=None,
        ge=0,
    )

    down_payment: float | None = Field(
        default=None,
        ge=0,
    )

    loan_original_amount: float | None = Field(
        default=None,
        ge=0,
    )

    loan_balance: float | None = Field(
        default=None,
        ge=0,
    )

    interest_rate: float | None = Field(
        default=None,
        ge=0,
    )

    monthly_payment: float | None = Field(
        default=None,
        ge=0,
    )

    monthly_rent: float | None = Field(
        default=None,
        ge=0,
    )

    monthly_expenses: float | None = Field(
        default=None,
        ge=0,
    )

    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=10,
    )

    purchase_date: date | None = None

    loan_end_date: date | None = None


class RealEstateResponse(
    RealEstateBase
):
    id: int

    equity: float
    annual_rent: float
    annual_expenses: float
    annual_loan_payments: float
    monthly_cash_flow: float
    annual_cash_flow: float
    gross_rental_yield: float
    net_rental_yield: float
    loan_to_value: float

    model_config = ConfigDict(
        from_attributes=True,
    )


class RealEstateSummary(BaseModel):
    properties_count: int
    total_current_value: float
    total_loan_balance: float
    total_equity: float
    total_monthly_rent: float
    total_monthly_expenses: float
    total_monthly_loan_payments: float
    total_monthly_cash_flow: float
    total_annual_cash_flow: float
    currency: str