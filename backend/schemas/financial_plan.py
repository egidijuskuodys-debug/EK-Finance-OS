from pydantic import (
    BaseModel,
    Field,
)


class FinancialPlanRequest(BaseModel):
    monthly_budget: float = Field(
        gt=0,
    )

    mortgage_share_percent: float = Field(
        default=0,
        ge=0,
        le=100,
    )

    expected_etf_return_percent: float = Field(
        default=7,
        ge=0,
        le=100,
    )

    projection_years: list[int] = Field(
        default=[
            1,
            5,
            10,
        ],
    )


class FinancialPlanProjection(BaseModel):
    years: int

    projected_investment_value: float

    additional_invested: float

    estimated_growth: float


class FinancialPlanAction(BaseModel):
    action: str

    monthly_amount: float

    description: str


class FinancialPlanResponse(BaseModel):
    base_currency: str

    monthly_budget: float

    monthly_investment_amount: float

    monthly_mortgage_amount: float

    mortgage_share_percent: float

    investment_share_percent: float

    expected_etf_return_percent: float

    current_investment_wealth: float

    annual_investment_amount: float

    projections: list[
        FinancialPlanProjection
    ]

    actions: list[
        FinancialPlanAction
    ]