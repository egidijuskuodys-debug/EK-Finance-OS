from sqlalchemy.orm import Session

from services.net_worth_projection_service import (
    get_net_worth_projection,
)
from services.real_estate_service import (
    get_real_estate_summary,
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

    real_estate_summary = (
        get_real_estate_summary(
            db
        )
    )

    rental_monthly_cash_flow = float(
        real_estate_summary[
            "total_monthly_cash_flow"
        ]
    )

    investment_income_target = max(
        monthly_income_target
        - rental_monthly_cash_flow,
        0.0,
    )

    required_capital = (
        investment_income_target
        * 12
        / withdrawal_rate
    )

    current_fi_capital = float(
        net_worth_projection[
            "starting_investment_value"
        ]
    )

    current_net_worth = float(
        net_worth_projection[
            "starting_net_worth"
        ]
    )

    current_real_estate_equity = float(
        net_worth_projection[
            "starting_real_estate_equity"
        ]
    )

    investment_monthly_passive_income = (
        current_fi_capital
        * withdrawal_rate
        / 12
    )

    current_monthly_passive_income = (
        investment_monthly_passive_income
        + rental_monthly_cash_flow
    )

    remaining_gap = max(
        required_capital
        - current_fi_capital,
        0.0,
    )

    if required_capital <= 0:
        progress_percent = 100.0
    else:
        progress_percent = min(
            (
                current_fi_capital
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

        investment_value = float(
            point["investment_value"]
        )

        real_estate_equity = float(
            point["real_estate_equity"]
        )

        net_worth = float(
            point["net_worth"]
        )

        investment_passive_income = (
            investment_value
            * withdrawal_rate
            / 12
        )

        monthly_passive_income = (
            investment_passive_income
            + rental_monthly_cash_flow
        )

        target_reached = (
            monthly_passive_income
            >= monthly_income_target
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
                "investment_value": round(
                    investment_value,
                    2,
                ),
                "real_estate_equity": round(
                    real_estate_equity,
                    2,
                ),
                "net_worth": round(
                    net_worth,
                    2,
                ),
                "investment_monthly_passive_income": (
                    round(
                        investment_passive_income,
                        2,
                    )
                ),
                "rental_monthly_cash_flow": round(
                    rental_monthly_cash_flow,
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
        "investment_income_target": round(
            investment_income_target,
            2,
        ),
        "required_capital": round(
            required_capital,
            2,
        ),
        "current_fi_capital": round(
            current_fi_capital,
            2,
        ),
        "current_net_worth": round(
            current_net_worth,
            2,
        ),
        "current_real_estate_equity": round(
            current_real_estate_equity,
            2,
        ),
        "investment_monthly_passive_income": (
            round(
                investment_monthly_passive_income,
                2,
            )
        ),
        "rental_monthly_cash_flow": round(
            rental_monthly_cash_flow,
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