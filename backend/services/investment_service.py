from sqlalchemy.orm import Session

from models.investment import Investment
from repositories import investment_repository
from schemas.investment import (
    InvestmentCreate,
    InvestmentUpdate,
)


def create_investment(
    db: Session,
    investment: InvestmentCreate,
):
    if investment_repository.exists_by_ticker(
        db,
        investment.ticker,
    ):
        raise ValueError(
            f"Investment with ticker '{investment.ticker}' already exists."
        )

    new_investment = Investment(
        broker=investment.broker,
        asset=investment.asset,
        ticker=investment.ticker,
        market_ticker=investment.market_ticker,
        asset_type=investment.asset_type,
        quantity=investment.quantity,
        purchase_price=investment.purchase_price,
        current_price=investment.current_price,
        currency=investment.currency,
        purchase_date=investment.purchase_date,
    )

    return investment_repository.create(
        db,
        new_investment,
    )


def get_investments(
    db: Session,
):
    return investment_repository.get_all(db)


def get_investment_by_id(
    db: Session,
    investment_id: int,
):
    return investment_repository.get_by_id(
        db,
        investment_id,
    )


def update_investment(
    db: Session,
    investment_id: int,
    investment_data: InvestmentUpdate,
):
    investment = investment_repository.get_by_id(
        db,
        investment_id,
    )

    if investment is None:
        return None

    update_data = investment_data.model_dump(
        exclude_unset=True,
    )

    if (
        "ticker" in update_data
        and update_data["ticker"] != investment.ticker
    ):
        if investment_repository.exists_by_ticker(
            db,
            update_data["ticker"],
        ):
            raise ValueError(
                f"Investment with ticker '{update_data['ticker']}' already exists."
            )

    return investment_repository.update_fields(
        db,
        investment,
        update_data,
    )


def delete_investment(
    db: Session,
    investment_id: int,
):
    investment = investment_repository.get_by_id(
        db,
        investment_id,
    )

    if investment is None:
        return None

    investment_repository.delete(
        db,
        investment,
    )

    return {
        "message": "Investment deleted successfully"
    }