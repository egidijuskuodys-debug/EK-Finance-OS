from sqlalchemy.orm import Session

from services.analytics_service import get_summary


DEFAULT_MILESTONE_YEARS = (5, 10, 15)


def _project_value(
    starting_value: float,
    monthly_contribution: float,
    monthly_rate: float,
    months: int,
) -> float:
    value = starting_value

    for _ in range(months):
        value = (
            value * (1 + monthly_rate)
            + monthly_contribution
        )

    return value


def get_portfolio_projection(
    db: Session,
    monthly_contribution: float,
    annual_return_percent: float,
):
    summary = get_summary(db)

    starting_value = float(
        summary.get(
            "portfolio_value",
            0.0,
        )
    )

    annual_rate = (
        annual_return_percent
        / 100
    )
    monthly_rate = (
        (1 + annual_rate) ** (1 / 12)
        - 1
    )

    milestones = []

    for years in DEFAULT_MILESTONE_YEARS:
        months = years * 12

        projected_value = _project_value(
            starting_value=starting_value,
            monthly_contribution=monthly_contribution,
            monthly_rate=monthly_rate,
            months=months,
        )

        total_contributions = (
            starting_value
            + monthly_contribution * months
        )

        investment_growth = (
            projected_value
            - total_contributions
        )

        milestones.append(
            {
                "years": years,
                "projected_value": round(
                    projected_value,
                    2,
                ),
                "total_contributions": round(
                    total_contributions,
                    2,
                ),
                "investment_growth": round(
                    investment_growth,
                    2,
                ),
            }
        )

    yearly_projection = []

    for years in range(
        0,
        max(DEFAULT_MILESTONE_YEARS) + 1,
    ):
        months = years * 12

        projected_value = _project_value(
            starting_value=starting_value,
            monthly_contribution=monthly_contribution,
            monthly_rate=monthly_rate,
            months=months,
        )

        yearly_projection.append(
            {
                "year": years,
                "value": round(
                    projected_value,
                    2,
                ),
            }
        )

    return {
        "currency": "EUR",
        "starting_value": round(
            starting_value,
            2,
        ),
        "monthly_contribution": round(
            monthly_contribution,
            2,
        ),
        "annual_return_percent": round(
            annual_return_percent,
            2,
        ),
        "milestones": milestones,
        "yearly_projection": yearly_projection,
    }