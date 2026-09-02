from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from models.investment import Investment
from repositories import investment_repository


def update_existing_investment_metadata(
    investment: Investment,
    investment_data: dict[str, Any],
) -> None:
    market_ticker = investment_data.get(
        "market_ticker"
    )

    if market_ticker:
        investment.market_ticker = market_ticker

    asset_type = investment_data.get(
        "asset_type"
    )

    if asset_type:
        investment.asset_type = asset_type

    asset = investment_data.get(
        "asset"
    )

    if asset:
        investment.asset = asset

    current_price = investment_data.get(
        "current_price"
    )

    if current_price is not None:
        investment.current_price = current_price

    db_currency = investment_data.get(
        "currency"
    )

    if (
        db_currency
        and db_currency != investment.currency
    ):
        raise ValueError(
            f"Currency mismatch for "
            f"{investment.ticker}: "
            f"database={investment.currency}, "
            f"import={db_currency}."
        )


def create_or_get_investment(
    db: Session,
    investment_data: dict[str, Any],
):
    broker = investment_data["broker"]
    ticker = investment_data["ticker"]

    existing_investment = (
        investment_repository
        .get_by_ticker_and_broker(
            db,
            ticker=ticker,
            broker=broker,
        )
    )

    if existing_investment is not None:
        update_existing_investment_metadata(
            existing_investment,
            investment_data,
        )

        db.flush()

        return existing_investment, False

    purchase_date = investment_data.get(
        "purchase_date"
    )

    if purchase_date is None:
        purchase_date = investment_data.get(
            "transaction_date"
        )

    if purchase_date is None:
        purchase_date = date.today()

    purchase_price = investment_data.get(
        "purchase_price"
    )

    if purchase_price is None:
        purchase_price = investment_data.get(
            "price",
            0,
        )

    quantity = investment_data.get(
        "quantity",
        0,
    )

    current_price = investment_data.get(
        "current_price"
    )

    if current_price is None:
        current_price = investment_data.get(
            "price",
            0,
        )

    investment = Investment(
        broker=broker,
        asset=investment_data.get(
            "asset",
            ticker,
        ),
        ticker=ticker,
        market_ticker=investment_data.get(
            "market_ticker",
            ticker,
        ),
        asset_type=investment_data.get(
            "asset_type",
            "Stock",
        ),
        quantity=quantity,
        purchase_price=purchase_price,
        current_price=current_price,
        currency=investment_data.get(
            "currency",
            "EUR",
        ),
        purchase_date=purchase_date,
    )

    investment_repository.add(
        db,
        investment,
    )

    return investment, True


def ensure_investments(
    db: Session,
    positions: list[dict[str, Any]],
    transactions: list[dict[str, Any]],
) -> dict[str, int]:
    created = 0
    existing = 0

    processed_keys: set[
        tuple[str, str]
    ] = set()

    position_lookup = {
        (
            position["broker"],
            position["ticker"],
        ): position
        for position in positions
    }

    for position in positions:
        key = (
            position["broker"],
            position["ticker"],
        )

        if key in processed_keys:
            continue

        _, was_created = (
            create_or_get_investment(
                db,
                position,
            )
        )

        processed_keys.add(key)

        if was_created:
            created += 1
        else:
            existing += 1

    for transaction in transactions:
        key = (
            transaction["broker"],
            transaction["ticker"],
        )

        if key in processed_keys:
            continue

        source_data = position_lookup.get(
            key,
            transaction,
        )

        _, was_created = (
            create_or_get_investment(
                db,
                source_data,
            )
        )

        processed_keys.add(key)

        if was_created:
            created += 1
        else:
            existing += 1

    return {
        "created": created,
        "existing": existing,
    }