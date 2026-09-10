from sqlalchemy.orm import Session

from models.real_estate import (
    RealEstateProperty,
)
from repositories import (
    real_estate_repository,
)
from schemas.real_estate import (
    RealEstateCreate,
    RealEstateUpdate,
)


def calculate_percentage(
    amount: float,
    base_value: float,
) -> float:
    if base_value <= 0:
        return 0.0

    return (
        amount
        / base_value
        * 100
    )


def serialize_property(
    property_record: RealEstateProperty,
):
    current_value = float(
        property_record.current_value
    )

    loan_balance = float(
        property_record.loan_balance
    )

    monthly_rent = float(
        property_record.monthly_rent
    )

    monthly_expenses = float(
        property_record.monthly_expenses
    )

    monthly_payment = float(
        property_record.monthly_payment
    )

    equity = (
        current_value
        - loan_balance
    )

    annual_rent = (
        monthly_rent
        * 12
    )

    annual_expenses = (
        monthly_expenses
        * 12
    )

    annual_loan_payments = (
        monthly_payment
        * 12
    )

    monthly_cash_flow = (
        monthly_rent
        - monthly_expenses
        - monthly_payment
    )

    annual_cash_flow = (
        monthly_cash_flow
        * 12
    )

    gross_rental_yield = (
        calculate_percentage(
            annual_rent,
            current_value,
        )
    )

    net_rental_yield = (
        calculate_percentage(
            annual_rent
            - annual_expenses,
            current_value,
        )
    )

    loan_to_value = (
        calculate_percentage(
            loan_balance,
            current_value,
        )
    )

    return {
        "id": property_record.id,
        "name": property_record.name,
        "address": (
            property_record.address
        ),
        "property_type": (
            property_record
            .property_type
        ),
        "purchase_price": round(
            float(
                property_record
                .purchase_price
            ),
            2,
        ),
        "current_value": round(
            current_value,
            2,
        ),
        "down_payment": round(
            float(
                property_record
                .down_payment
            ),
            2,
        ),
        "loan_original_amount": round(
            float(
                property_record
                .loan_original_amount
            ),
            2,
        ),
        "loan_balance": round(
            loan_balance,
            2,
        ),
        "interest_rate": (
            round(
                float(
                    property_record
                    .interest_rate
                ),
                4,
            )
            if (
                property_record
                .interest_rate
                is not None
            )
            else None
        ),
        "monthly_payment": round(
            monthly_payment,
            2,
        ),
        "monthly_rent": round(
            monthly_rent,
            2,
        ),
        "monthly_expenses": round(
            monthly_expenses,
            2,
        ),
        "currency": (
            property_record.currency
        ),
        "purchase_date": (
            property_record
            .purchase_date
        ),
        "loan_end_date": (
            property_record
            .loan_end_date
        ),
        "equity": round(
            equity,
            2,
        ),
        "annual_rent": round(
            annual_rent,
            2,
        ),
        "annual_expenses": round(
            annual_expenses,
            2,
        ),
        "annual_loan_payments": round(
            annual_loan_payments,
            2,
        ),
        "monthly_cash_flow": round(
            monthly_cash_flow,
            2,
        ),
        "annual_cash_flow": round(
            annual_cash_flow,
            2,
        ),
        "gross_rental_yield": round(
            gross_rental_yield,
            2,
        ),
        "net_rental_yield": round(
            net_rental_yield,
            2,
        ),
        "loan_to_value": round(
            loan_to_value,
            2,
        ),
    }


def get_all_properties(
    db: Session,
):
    property_records = (
        real_estate_repository
        .get_all_properties(
            db
        )
    )

    return [
        serialize_property(
            property_record
        )
        for property_record
        in property_records
    ]


def get_property_by_id(
    db: Session,
    property_id: int,
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

    return serialize_property(
        property_record
    )


def create_property(
    db: Session,
    property_data: RealEstateCreate,
):
    property_record = (
        real_estate_repository
        .create_property(
            db,
            property_data,
        )
    )

    return serialize_property(
        property_record
    )


def update_property(
    db: Session,
    property_id: int,
    property_data: RealEstateUpdate,
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

    updated_property = (
        real_estate_repository
        .update_property(
            db,
            property_record,
            property_data,
        )
    )

    return serialize_property(
        updated_property
    )


def delete_property(
    db: Session,
    property_id: int,
) -> bool:
    property_record = (
        real_estate_repository
        .get_property_by_id(
            db,
            property_id,
        )
    )

    if property_record is None:
        return False

    real_estate_repository.delete_property(
        db,
        property_record,
    )

    return True


def get_real_estate_summary(
    db: Session,
):
    properties = (
        get_all_properties(
            db
        )
    )

    total_current_value = sum(
        property_data[
            "current_value"
        ]
        for property_data
        in properties
    )

    total_loan_balance = sum(
        property_data[
            "loan_balance"
        ]
        for property_data
        in properties
    )

    total_equity = sum(
        property_data[
            "equity"
        ]
        for property_data
        in properties
    )

    total_monthly_rent = sum(
        property_data[
            "monthly_rent"
        ]
        for property_data
        in properties
    )

    total_monthly_expenses = sum(
        property_data[
            "monthly_expenses"
        ]
        for property_data
        in properties
    )

    total_monthly_loan_payments = sum(
        property_data[
            "monthly_payment"
        ]
        for property_data
        in properties
    )

    total_monthly_cash_flow = sum(
        property_data[
            "monthly_cash_flow"
        ]
        for property_data
        in properties
    )

    currency = (
        properties[0]["currency"]
        if properties
        else "EUR"
    )

    return {
        "properties_count": len(
            properties
        ),
        "total_current_value": round(
            total_current_value,
            2,
        ),
        "total_loan_balance": round(
            total_loan_balance,
            2,
        ),
        "total_equity": round(
            total_equity,
            2,
        ),
        "total_monthly_rent": round(
            total_monthly_rent,
            2,
        ),
        "total_monthly_expenses": round(
            total_monthly_expenses,
            2,
        ),
        "total_monthly_loan_payments": (
            round(
                total_monthly_loan_payments,
                2,
            )
        ),
        "total_monthly_cash_flow": round(
            total_monthly_cash_flow,
            2,
        ),
        "total_annual_cash_flow": round(
            total_monthly_cash_flow
            * 12,
            2,
        ),
        "currency": currency,
    }