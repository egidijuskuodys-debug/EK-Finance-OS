from schemas.financial_plan import (
    FinancialPlanAction,
    FinancialPlanProjection,
    FinancialPlanRequest,
    FinancialPlanResponse,
)


BASE_CURRENCY = "EUR"


def calculate_future_value(
    current_value: float,
    monthly_contribution: float,
    annual_return_percent: float,
    years: int,
) -> float:
    months = years * 12

    monthly_rate = (
        annual_return_percent
        / 100
        / 12
    )

    future_current_value = (
        current_value
        * (1 + monthly_rate) ** months
    )

    if monthly_rate == 0:
        future_contributions = (
            monthly_contribution
            * months
        )
    else:
        future_contributions = (
            monthly_contribution
            * (
                (
                    (1 + monthly_rate) ** months
                    - 1
                )
                / monthly_rate
            )
        )

    return (
        future_current_value
        + future_contributions
    )


def build_financial_plan(
    request: FinancialPlanRequest,
    current_investment_wealth: float,
) -> FinancialPlanResponse:
    monthly_mortgage_amount = (
        request.monthly_budget
        * request.mortgage_share_percent
        / 100
    )

    monthly_investment_amount = (
        request.monthly_budget
        - monthly_mortgage_amount
    )

    investment_share_percent = (
        100
        - request.mortgage_share_percent
    )

    annual_investment_amount = (
        monthly_investment_amount
        * 12
    )

    projections = []

    for years in sorted(
        set(request.projection_years)
    ):
        if years <= 0:
            continue

        projected_value = (
            calculate_future_value(
                current_value=(
                    current_investment_wealth
                ),
                monthly_contribution=(
                    monthly_investment_amount
                ),
                annual_return_percent=(
                    request
                    .expected_etf_return_percent
                ),
                years=years,
            )
        )

        additional_invested = (
            monthly_investment_amount
            * 12
            * years
        )

        estimated_growth = (
            projected_value
            - current_investment_wealth
            - additional_invested
        )

        projections.append(
            FinancialPlanProjection(
                years=years,
                projected_investment_value=round(
                    projected_value,
                    2,
                ),
                additional_invested=round(
                    additional_invested,
                    2,
                ),
                estimated_growth=round(
                    estimated_growth,
                    2,
                ),
            )
        )

    actions = []

    if monthly_investment_amount > 0:
        actions.append(
            FinancialPlanAction(
                action="INVEST",
                monthly_amount=round(
                    monthly_investment_amount,
                    2,
                ),
                description=(
                    "Allocate this amount to "
                    "the investment portfolio "
                    "each month."
                ),
            )
        )

    if monthly_mortgage_amount > 0:
        actions.append(
            FinancialPlanAction(
                action="MORTGAGE",
                monthly_amount=round(
                    monthly_mortgage_amount,
                    2,
                ),
                description=(
                    "Allocate this amount to "
                    "additional mortgage "
                    "repayment each month."
                ),
            )
        )

    return FinancialPlanResponse(
        base_currency=BASE_CURRENCY,
        monthly_budget=round(
            request.monthly_budget,
            2,
        ),
        monthly_investment_amount=round(
            monthly_investment_amount,
            2,
        ),
        monthly_mortgage_amount=round(
            monthly_mortgage_amount,
            2,
        ),
        mortgage_share_percent=round(
            request.mortgage_share_percent,
            2,
        ),
        investment_share_percent=round(
            investment_share_percent,
            2,
        ),
        expected_etf_return_percent=round(
            request.expected_etf_return_percent,
            2,
        ),
        current_investment_wealth=round(
            current_investment_wealth,
            2,
        ),
        annual_investment_amount=round(
            annual_investment_amount,
            2,
        ),
        projections=projections,
        actions=actions,
    )