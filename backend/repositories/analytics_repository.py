from collections import defaultdict

from sqlalchemy.orm import Session

from models.investment import Investment
from models.transaction import Transaction
from services.fx_service import (
    BASE_CURRENCY,
    convert_to_base_currency,
)


def get_total_positions(
    db: Session,
):
    return db.query(
        Investment
    ).count()


def get_all_investments(
    db: Session,
):
    return db.query(
        Investment
    ).all()


def get_total_value(
    db: Session,
):
    investments = get_all_investments(
        db
    )

    total_value = 0.0

    for investment in investments:
        local_value = (
            investment.quantity
            * investment.current_price
        )

        total_value += (
            convert_to_base_currency(
                amount=local_value,
                currency=investment.currency,
            )
        )

    return total_value


def get_total_invested(
    db: Session,
):
    investments = get_all_investments(
        db
    )

    total_invested = 0.0

    for investment in investments:
        local_invested = (
            investment.quantity
            * investment.purchase_price
        )

        total_invested += (
            convert_to_base_currency(
                amount=local_invested,
                currency=investment.currency,
            )
        )

    return total_invested


def get_total_realized_profit(
    db: Session,
):
    rows = (
        db.query(
            Transaction.realized_profit,
            Transaction.currency,
            Transaction.fx_rate,
        )
        .all()
    )

    total_realized_profit = 0.0

    for (
        realized_profit,
        currency,
        fx_rate,
    ) in rows:
        if realized_profit is None:
            continue

        realized_profit = float(
            realized_profit
        )

        currency = (
            currency
            .strip()
            .upper()
        )

        if currency == BASE_CURRENCY:
            total_realized_profit += (
                realized_profit
            )
            continue

        if (
            fx_rate is not None
            and float(fx_rate) > 0
        ):
            total_realized_profit += (
                realized_profit
                / float(fx_rate)
            )
            continue

        total_realized_profit += (
            convert_to_base_currency(
                amount=realized_profit,
                currency=currency,
            )
        )

    return total_realized_profit


def get_value_by_broker(
    db: Session,
):
    investments = get_all_investments(
        db
    )

    broker_values = defaultdict(
        float
    )

    for investment in investments:
        local_value = (
            investment.quantity
            * investment.current_price
        )

        base_value = (
            convert_to_base_currency(
                amount=local_value,
                currency=investment.currency,
            )
        )

        broker_values[
            investment.broker
        ] += base_value

    return sorted(
        broker_values.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def get_value_by_asset_type(
    db: Session,
):
    investments = get_all_investments(
        db
    )

    asset_type_values = defaultdict(
        float
    )

    for investment in investments:
        local_value = (
            investment.quantity
            * investment.current_price
        )

        base_value = (
            convert_to_base_currency(
                amount=local_value,
                currency=investment.currency,
            )
        )

        asset_type_values[
            investment.asset_type
        ] += base_value

    return sorted(
        asset_type_values.items(),
        key=lambda item: item[1],
        reverse=True,
    )


def get_portfolio_currencies(
    db: Session,
):
    currencies = (
        db.query(
            Investment.currency
        )
        .distinct()
        .all()
    )

    return sorted(
        currency
        for (currency,) in currencies
        if currency
    )


def get_base_currency():
    return BASE_CURRENCY