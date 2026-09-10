from sqlalchemy.orm import Session

from services.portfolio_projection_service import (
    get_portfolio_projection,
)
from services.real_estate_projection_service import (
    get_real_estate_projection,
)
from services.real_estate_service import (
    get_all_properties,
)


PROJECTION_YEARS = 15


def get_net_worth_projection(
    db: Session,
    monthly_contribution: float,
    annual_return_percent: float,
    annual_property_growth: float,
):
    portfolio_projection = (
        get_portfolio_projection(
            db=db,
            monthly_contribution=(
                monthly_contribution
            ),
            annual_return_percent=(
                annual_return_percent
            ),
        )
    )

    properties = get_all_properties(
        db
    )

    property_projections = []

    for property_data in properties:
        projection = (
            get_real_estate_projection(
                db=db,
                property_id=(
                    property_data["id"]
                ),
                annual_property_growth=(
                    annual_property_growth
                ),
                projection_years=(
                    PROJECTION_YEARS
                ),
            )
        )

        if projection is not None:
            property_projections.append(
                projection
            )

    yearly_projection = []

    for portfolio_point in (
        portfolio_projection[
            "yearly_projection"
        ]
    ):
        year = int(
            portfolio_point["year"]
        )

        real_estate_value = 0.0
        real_estate_loan_balance = 0.0
        real_estate_equity = 0.0

        for property_projection in (
            property_projections
        ):
            property_point = next(
                (
                    point
                    for point
                    in property_projection[
                        "points"
                    ]
                    if point["year"]
                    == year
                ),
                None,
            )

            if property_point is None:
                continue

            real_estate_value += float(
                property_point[
                    "property_value"
                ]
            )

            real_estate_loan_balance += (
                float(
                    property_point[
                        "loan_balance"
                    ]
                )
            )

            real_estate_equity += float(
                property_point[
                    "equity"
                ]
            )

        investment_value = float(
            portfolio_point["value"]
        )

        net_worth = (
            investment_value
            + real_estate_equity
        )

        yearly_projection.append(
            {
                "year": year,
                "investment_value": round(
                    investment_value,
                    2,
                ),
                "real_estate_value": round(
                    real_estate_value,
                    2,
                ),
                "real_estate_loan_balance": (
                    round(
                        real_estate_loan_balance,
                        2,
                    )
                ),
                "real_estate_equity": round(
                    real_estate_equity,
                    2,
                ),
                "net_worth": round(
                    net_worth,
                    2,
                ),
            }
        )

    starting_point = (
        yearly_projection[0]
    )

    final_point = (
        yearly_projection[-1]
    )

    return {
        "currency": (
            portfolio_projection[
                "currency"
            ]
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
        "projection_years": (
            PROJECTION_YEARS
        ),
        "starting_investment_value": (
            starting_point[
                "investment_value"
            ]
        ),
        "starting_real_estate_equity": (
            starting_point[
                "real_estate_equity"
            ]
        ),
        "starting_net_worth": (
            starting_point[
                "net_worth"
            ]
        ),
        "final_investment_value": (
            final_point[
                "investment_value"
            ]
        ),
        "final_real_estate_equity": (
            final_point[
                "real_estate_equity"
            ]
        ),
        "final_net_worth": (
            final_point[
                "net_worth"
            ]
        ),
        "yearly_projection": (
            yearly_projection
        ),
    }