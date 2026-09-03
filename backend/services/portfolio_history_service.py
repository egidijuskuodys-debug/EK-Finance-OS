from collections import defaultdict
from datetime import date

from sqlalchemy.orm import Session

from models.investment import Investment
from models.price_history import PriceHistory
from models.transaction import Transaction
from services.fx_service import (
    get_historical_fx_rate,
)


QUANTITY_EPSILON = 0.0001


def get_portfolio_history(
    db: Session,
) -> list[dict]:
    investments = (
        db.query(Investment)
        .order_by(Investment.id)
        .all()
    )

    if not investments:
        return []

    transactions = (
        db.query(Transaction)
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    price_rows = (
        db.query(PriceHistory)
        .order_by(
            PriceHistory.price_date,
            PriceHistory.id,
        )
        .all()
    )

    if not transactions or not price_rows:
        return []

    transactions_by_date = defaultdict(
        list
    )

    for transaction in transactions:
        transactions_by_date[
            transaction.transaction_date
        ].append(transaction)

    prices_by_date = defaultdict(
        list
    )

    for price_row in price_rows:
        prices_by_date[
            price_row.price_date
        ].append(price_row)

    all_dates = sorted(
        prices_by_date.keys()
    )

    quantities: dict[int, float] = (
        defaultdict(float)
    )

    latest_prices: dict[
        int,
        PriceHistory,
    ] = {}

    investment_lookup = {
        investment.id: investment
        for investment in investments
    }

    history = []

    transaction_dates = sorted(
        transactions_by_date.keys()
    )

    transaction_index = 0

    for current_date in all_dates:
        while (
            transaction_index
            < len(transaction_dates)
            and transaction_dates[
                transaction_index
            ]
            <= current_date
        ):
            transaction_date = (
                transaction_dates[
                    transaction_index
                ]
            )

            for transaction in (
                transactions_by_date[
                    transaction_date
                ]
            ):
                investment_id = (
                    transaction.investment_id
                )

                transaction_type = (
                    transaction.transaction_type
                    .strip()
                    .upper()
                )

                if transaction_type == "BUY":
                    quantities[
                        investment_id
                    ] += transaction.quantity

                elif transaction_type == "SELL":
                    quantities[
                        investment_id
                    ] -= transaction.quantity

                if (
                    abs(
                        quantities[
                            investment_id
                        ]
                    )
                    < QUANTITY_EPSILON
                ):
                    quantities[
                        investment_id
                    ] = 0.0

            transaction_index += 1

        for price_row in (
            prices_by_date[current_date]
        ):
            latest_prices[
                price_row.investment_id
            ] = price_row

        total_value_eur = 0.0
        positions_count = 0

        for (
            investment_id,
            quantity,
        ) in quantities.items():
            if quantity <= QUANTITY_EPSILON:
                continue

            price_row = latest_prices.get(
                investment_id
            )

            if price_row is None:
                continue

            investment = (
                investment_lookup.get(
                    investment_id
                )
            )

            if investment is None:
                continue

            position_value = (
                quantity
                * price_row.close_price
            )

            currency = (
                price_row.currency
                .strip()
                .upper()
            )

            if currency != "EUR":
                fx_rate = (
                    get_historical_fx_rate(
                        from_currency=currency,
                        rate_date=current_date,
                        to_currency="EUR",
                    )
                )

                position_value *= fx_rate

            total_value_eur += (
                position_value
            )

            positions_count += 1

        history.append(
            {
                "date": current_date,
                "value_eur": round(
                    total_value_eur,
                    2,
                ),
                "positions": (
                    positions_count
                ),
            }
        )

    return history