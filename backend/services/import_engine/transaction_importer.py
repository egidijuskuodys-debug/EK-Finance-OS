from typing import Any

from sqlalchemy.orm import Session

from models.transaction import Transaction
from repositories import (
    investment_repository,
    transaction_repository,
)
from services.transaction_service import (
    recalculate_position,
)


def import_transactions(
    db: Session,
    transactions: list[dict[str, Any]],
) -> dict[str, int]:
    imported = 0
    skipped = 0

    affected_investment_ids: set[int] = set()

    for transaction_data in transactions:
        broker = transaction_data["broker"]
        ticker = transaction_data["ticker"]

        investment = (
            investment_repository
            .get_by_ticker_and_broker(
                db,
                ticker=ticker,
                broker=broker,
            )
        )

        if investment is None:
            raise ValueError(
                f"Investment not found for "
                f"{broker} / {ticker}."
            )

        broker_transaction_id = (
            transaction_data.get(
                "broker_transaction_id"
            )
        )

        if not broker_transaction_id:
            raise ValueError(
                "Imported transaction does not have "
                "broker_transaction_id."
            )

        duplicate_exists = (
            transaction_repository
            .exists_by_broker_transaction_id(
                db,
                broker_transaction_id,
            )
        )

        if duplicate_exists:
            skipped += 1
            continue

        currency = transaction_data.get(
            "currency",
            investment.currency,
        )

        if currency != investment.currency:
            raise ValueError(
                f"Currency mismatch for {ticker}: "
                f"transaction={currency}, "
                f"investment={investment.currency}."
            )

        commission = transaction_data.get(
            "commission",
            0,
        )

        if commission is None:
            commission = 0

        commission = abs(
            float(commission)
        )

        fx_rate = transaction_data.get(
            "fx_rate"
        )

        if fx_rate is not None:
            fx_rate = float(
                fx_rate
            )

            if fx_rate <= 0:
                raise ValueError(
                    f"Invalid FX rate for "
                    f"{broker} / {ticker}: "
                    f"{fx_rate}."
                )

        transaction = Transaction(
            investment_id=investment.id,
            broker_transaction_id=(
                broker_transaction_id
            ),
            transaction_type=(
                transaction_data[
                    "transaction_type"
                ]
            ),
            quantity=transaction_data[
                "quantity"
            ],
            price=transaction_data[
                "price"
            ],
            commission=commission,
            realized_profit=0,
            currency=currency,
            fx_rate=fx_rate,
            transaction_date=(
                transaction_data[
                    "transaction_date"
                ]
            ),
        )

        transaction_repository.add(
            db,
            transaction,
        )

        affected_investment_ids.add(
            investment.id
        )

        imported += 1

    for investment_id in sorted(
        affected_investment_ids
    ):
        recalculate_position(
            db,
            investment_id,
        )

    return {
        "imported": imported,
        "skipped": skipped,
    }