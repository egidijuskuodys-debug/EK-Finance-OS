from sqlalchemy.orm import Session

from models.dividend import Dividend
from repositories import (
    dividend_repository,
    investment_repository,
)
from schemas.dividend_schema import (
    DividendCreate,
    DividendUpdate,
)


def get_dividends(db: Session):
    return dividend_repository.get_all(db)


def get_dividend_by_id(
    db: Session,
    dividend_id: int,
):
    return dividend_repository.get_by_id(
        db,
        dividend_id,
    )


def get_dividends_by_investment(
    db: Session,
    investment_id: int,
):
    investment = investment_repository.get_by_id(
        db,
        investment_id,
    )

    if investment is None:
        raise ValueError("Investment not found.")

    return dividend_repository.get_by_investment_id(
        db,
        investment_id,
    )


def create_dividend(
    db: Session,
    dividend_data: DividendCreate,
):
    investment = investment_repository.get_by_id(
        db,
        dividend_data.investment_id,
    )

    if investment is None:
        raise ValueError("Investment not found.")

    if dividend_data.currency != investment.currency:
        raise ValueError(
            "Dividend currency must match "
            "investment currency."
        )

    net_amount = (
        dividend_data.net_amount
        if dividend_data.net_amount is not None
        else dividend_data.gross_amount
        - dividend_data.tax_amount
    )

    if dividend_data.tax_amount > dividend_data.gross_amount:
        raise ValueError(
            "Tax amount cannot exceed gross amount."
        )

    if net_amount < 0:
        raise ValueError(
            "Net amount cannot be negative."
        )

    dividend = Dividend(
        investment_id=dividend_data.investment_id,
        payment_date=dividend_data.payment_date,
        gross_amount=dividend_data.gross_amount,
        tax_amount=dividend_data.tax_amount,
        net_amount=round(net_amount, 2),
        currency=dividend_data.currency,
        notes=dividend_data.notes,
    )

    return dividend_repository.create(
        db,
        dividend,
    )


def update_dividend(
    db: Session,
    dividend_id: int,
    dividend_data: DividendUpdate,
):
    dividend = dividend_repository.get_by_id(
        db,
        dividend_id,
    )

    if dividend is None:
        return None

    update_data = dividend_data.model_dump(
        exclude_unset=True,
    )

    investment_id = update_data.get(
        "investment_id",
        dividend.investment_id,
    )

    investment = investment_repository.get_by_id(
        db,
        investment_id,
    )

    if investment is None:
        raise ValueError("Investment not found.")

    gross_amount = update_data.get(
        "gross_amount",
        dividend.gross_amount,
    )

    tax_amount = update_data.get(
        "tax_amount",
        dividend.tax_amount,
    )

    currency = update_data.get(
        "currency",
        dividend.currency,
    )

    if currency != investment.currency:
        raise ValueError(
            "Dividend currency must match "
            "investment currency."
        )

    if tax_amount > gross_amount:
        raise ValueError(
            "Tax amount cannot exceed gross amount."
        )

    if (
        "gross_amount" in update_data
        or "tax_amount" in update_data
    ) and "net_amount" not in update_data:
        update_data["net_amount"] = round(
            gross_amount - tax_amount,
            2,
        )

    net_amount = update_data.get(
        "net_amount",
        dividend.net_amount,
    )

    if net_amount < 0:
        raise ValueError(
            "Net amount cannot be negative."
        )

    return dividend_repository.update_fields(
        db,
        dividend,
        update_data,
    )


def delete_dividend(
    db: Session,
    dividend_id: int,
):
    dividend = dividend_repository.get_by_id(
        db,
        dividend_id,
    )

    if dividend is None:
        return None

    dividend_repository.delete(
        db,
        dividend,
    )

    return {
        "message": "Dividend deleted successfully"
    }