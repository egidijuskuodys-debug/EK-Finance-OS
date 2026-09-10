from sqlalchemy.orm import Session

from services.net_worth_projection_service import (
    get_net_worth_projection,
)


def get_financial_independence_projection(
    db: Session,
    monthly_income_target: float,
    withdrawal_rate_percent: float,
    monthly_contribution: float,
    annual_return_percent: float,
    annual_property_growth: float,
    current_age: int,
):
    annual_income_target = (
        monthly_income_target
        * 12
    )

    withdrawal_rate = (
        withdrawal_rate_percent
        / 100
    )

    required_capital = (
        annual_income_target
        / withdrawal_rate
    )

    net_worth_projection = (
        get_net_worth_projection(
            db=db,
            monthly_contribution=(
                monthly_contribution
            ),
            annual_return_percent=(
                annual_return_percent
            ),
            annual_property_growth=(
                annual_property_growth
            ),
        )
    )

    current_net_worth = float(
        net_worth_projection[
            "starting_net_worth"
        ]
    )

    current_monthly_passive_income = (
        current_net_worth
        * withdrawal_rate
        / 12
    )

    remaining_gap = max(
        required_capital
        - current_net_worth,
        0.0,
    )

    progress_percent = min(
        (
            current_net_worth
            / required_capital
            * 100
        ),
        100.0,
    )

    years_to_goal = None
    projected_age_at_goal = None

    yearly_projection = []

    for point in (
        net_worth_projection[
            "yearly_projection"
        ]
    ):
        year = int(
            point["year"]
        )

        net_worth = float(
            point["net_worth"]
        )

        monthly_passive_income = (
            net_worth
            * withdrawal_rate
            / 12
        )

        target_reached = (
            net_worth
            >= required_capital
        )

        if (
            target_reached
            and years_to_goal is None
        ):
            years_to_goal = year

            projected_age_at_goal = (
                current_age
                + year
            )

        yearly_projection.append(
            {
                "year": year,
                "net_worth": round(
                    net_worth,
                    2,
                ),
                "monthly_passive_income": (
                    round(
                        monthly_passive_income,
                        2,
                    )
                ),
                "target_reached": (
                    target_reached
                ),
            }
        )

    return {
        "currency": (
            net_worth_projection[
                "currency"
            ]
        ),
        "monthly_income_target": round(
            monthly_income_target,
            2,
        ),
        "annual_income_target": round(
            annual_income_target,
            2,
        ),
        "withdrawal_rate_percent": round(
            withdrawal_rate_percent,
            2,
        ),
        "required_capital": round(
            required_capital,
            2,
        ),
        "current_net_worth": round(
            current_net_worth,
            2,
        ),
        "current_monthly_passive_income": (
            round(
                current_monthly_passive_income,
                2,
            )
        ),
        "remaining_gap": round(
            remaining_gap,
            2,
        ),
        "progress_percent": round(
            progress_percent,
            2,
        ),
        "years_to_goal": (
            years_to_goal
        ),
        "current_age": (
            current_age
        ),
        "projected_age_at_goal": (
            projected_age_at_goal
        ),
        "monthly_contribution": round(
            monthly_contribution,
            2,
        ),
        "annual_return_percent": round(
            annual_return_percent,
            2,
        ),
        "annual_property_growth": round(
            annual_property_growth,
            2,
        ),
        "yearly_projection": (
            yearly_projection
        ),
    }