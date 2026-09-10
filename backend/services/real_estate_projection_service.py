import calendar
from datetime import date

from sqlalchemy.orm import Session

from repositories import (
    real_estate_repository,
)


def add_months(
    source_date: date,
    months: int,
) -> date:
    month_index = (
        source_date.month
        - 1
        + months
    )

    year = (
        source_date.year
        + month_index // 12
    )

    month = (
        month_index % 12
        + 1
    )

    last_day = calendar.monthrange(
        year,
        month,
    )[1]

    day = min(
        source_date.day,
        last_day,
    )

    return date(
        year,
        month,
        day,
    )


def get_real_estate_projection(
    db: Session,
    property_id: int,
    annual_property_growth: float,
    projection_years: int,
):
    property_record = (
        real_estate_repository
        .get_property_by_id(
            db,
            property_id,
        )
    )

    if property_record is None:
        return None

    current_date = date.today()

    property_value = float(
        property_record.current_value
    )

    initial_loan_balance = float(
        property_record.loan_balance
    )

    loan_balance = (
        initial_loan_balance
    )

    annual_interest_rate = float(
        property_record.interest_rate
        or 0.0
    )

    monthly_payment = float(
        property_record.monthly_payment
    )

    loan_end_date = (
        property_record.loan_end_date
    )

    monthly_interest_rate = (
        annual_interest_rate
        / 100
        / 12
    )

    monthly_property_growth = (
        (
            1
            + annual_property_growth
            / 100
        )
        ** (
            1
            / 12
        )
        - 1
    )

    total_principal_paid = 0.0
    total_interest_paid = 0.0

    points = [
        {
            "year": 0,
            "projection_date": (
                current_date
            ),
            "property_value": round(
                property_value,
                2,
            ),
            "loan_balance": round(
                loan_balance,
                2,
            ),
            "equity": round(
                property_value
                - loan_balance,
                2,
            ),
            "principal_paid": 0.0,
            "interest_paid": 0.0,
        }
    ]

    total_months = (
        projection_years
        * 12
    )

    for month_number in range(
        1,
        total_months + 1,
    ):
        projection_date = add_months(
            current_date,
            month_number,
        )

        property_value *= (
            1
            + monthly_property_growth
        )

        if loan_balance > 0:
            interest_amount = (
                loan_balance
                * monthly_interest_rate
            )

            principal_amount = max(
                monthly_payment
                - interest_amount,
                0.0,
            )

            principal_amount = min(
                principal_amount,
                loan_balance,
            )

            if (
                loan_end_date is not None
                and projection_date
                >= loan_end_date
            ):
                principal_amount = (
                    loan_balance
                )

            loan_balance -= (
                principal_amount
            )

            total_principal_paid += (
                principal_amount
            )

            total_interest_paid += (
                interest_amount
            )

        if month_number % 12 == 0:
            points.append(
                {
                    "year": (
                        month_number
                        // 12
                    ),
                    "projection_date": (
                        projection_date
                    ),
                    "property_value": round(
                        property_value,
                        2,
                    ),
                    "loan_balance": round(
                        max(
                            loan_balance,
                            0.0,
                        ),
                        2,
                    ),
                    "equity": round(
                        property_value
                        - max(
                            loan_balance,
                            0.0,
                        ),
                        2,
                    ),
                    "principal_paid": round(
                        total_principal_paid,
                        2,
                    ),
                    "interest_paid": round(
                        total_interest_paid,
                        2,
                    ),
                }
            )

    return {
        "property_id": (
            property_record.id
        ),
        "property_name": (
            property_record.name
        ),
        "currency": (
            property_record.currency
        ),
        "annual_property_growth": round(
            annual_property_growth,
            2,
        ),
        "annual_interest_rate": round(
            annual_interest_rate,
            4,
        ),
        "monthly_payment": round(
            monthly_payment,
            2,
        ),
        "loan_end_date": (
            loan_end_date
        ),
        "projection_years": (
            projection_years
        ),
        "total_principal_paid": round(
            total_principal_paid,
            2,
        ),
        "total_interest_paid": round(
            total_interest_paid,
            2,
        ),
        "points": points,
    }