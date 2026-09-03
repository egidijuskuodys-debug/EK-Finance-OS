from collections import defaultdict

from sqlalchemy.orm import Session

from models.cash_movement import CashMovement
from models.dividend import Dividend
from models.investment import Investment
from models.transaction import Transaction
from services.cash_flow_service import (
    DEPOSIT_TYPES,
    WITHDRAWAL_TYPES,
    normalize_movement_type,
)
from services.fx_service import (
    BASE_CURRENCY,
    convert_to_base_currency,
)


INTERNAL_CASH_INCOME_TYPES = {
    "REWARD",
    "POSITION CLOSURE",
}

SIGNED_CASH_MOVEMENT_TYPES = {
    "FOREX",
}


def normalize_currency(
    currency: str,
) -> str:
    return (
        str(currency)
        .strip()
        .upper()
    )


def add_currency_balance(
    balances: dict[str, float],
    currency: str,
    amount: float,
) -> None:
    normalized_currency = (
        normalize_currency(
            currency
        )
    )

    balances[
        normalized_currency
    ] += float(amount)


def convert_current_balance_to_base(
    amount: float,
    currency: str,
) -> float:
    normalized_currency = (
        normalize_currency(
            currency
        )
    )

    if (
        normalized_currency
        == BASE_CURRENCY
    ):
        return float(amount)

    return convert_to_base_currency(
        amount=float(amount),
        currency=normalized_currency,
    )


def get_cash_balance(
    db: Session,
):
    broker_balances = defaultdict(
        lambda: defaultdict(float)
    )

    broker_stats = defaultdict(
        lambda: {
            "deposits": 0.0,
            "withdrawals": 0.0,
            "buys": 0.0,
            "sells": 0.0,
            "commissions": 0.0,
            "dividends": 0.0,
            "other_income": 0.0,
        }
    )

    cash_movements = (
        db.query(CashMovement)
        .order_by(
            CashMovement.movement_date,
            CashMovement.id,
        )
        .all()
    )

    for movement in cash_movements:
        broker = movement.broker

        movement_type = (
            normalize_movement_type(
                movement.movement_type
            )
        )

        currency = normalize_currency(
            movement.currency
        )

        amount = float(
            movement.amount
        )

        balances = broker_balances[
            broker
        ]

        stats = broker_stats[
            broker
        ]

        if (
            movement_type
            in SIGNED_CASH_MOVEMENT_TYPES
        ):
            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=amount,
            )

        elif movement_type in DEPOSIT_TYPES:
            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=abs(amount),
            )

            stats["deposits"] += (
                convert_current_balance_to_base(
                    amount=abs(amount),
                    currency=currency,
                )
            )

        elif (
            movement_type
            in WITHDRAWAL_TYPES
        ):
            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=-abs(amount),
            )

            stats[
                "withdrawals"
            ] += (
                convert_current_balance_to_base(
                    amount=abs(amount),
                    currency=currency,
                )
            )

        elif (
            movement_type
            in INTERNAL_CASH_INCOME_TYPES
        ):
            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=amount,
            )

            stats[
                "other_income"
            ] += (
                convert_current_balance_to_base(
                    amount=amount,
                    currency=currency,
                )
            )

    transactions = (
        db.query(Transaction)
        .join(
            Investment,
            Transaction.investment_id
            == Investment.id,
        )
        .order_by(
            Transaction.transaction_date,
            Transaction.id,
        )
        .all()
    )

    for transaction in transactions:
        investment = (
            transaction.investment
        )

        if investment is None:
            continue

        broker = investment.broker

        transaction_type = (
            transaction.transaction_type
            .strip()
            .upper()
        )

        currency = normalize_currency(
            transaction.currency
        )

        gross_amount = (
            float(transaction.quantity)
            * float(transaction.price)
        )

        commission = abs(
            float(
                transaction.commission
                or 0.0
            )
        )

        balances = broker_balances[
            broker
        ]

        stats = broker_stats[
            broker
        ]

        if transaction_type == "BUY":
            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=-gross_amount,
            )

            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=-commission,
            )

            stats["buys"] += (
                convert_current_balance_to_base(
                    amount=gross_amount,
                    currency=currency,
                )
            )

            stats[
                "commissions"
            ] += (
                convert_current_balance_to_base(
                    amount=commission,
                    currency=currency,
                )
            )

        elif transaction_type == "SELL":
            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=gross_amount,
            )

            add_currency_balance(
                balances=balances,
                currency=currency,
                amount=-commission,
            )

            stats["sells"] += (
                convert_current_balance_to_base(
                    amount=gross_amount,
                    currency=currency,
                )
            )

            stats[
                "commissions"
            ] += (
                convert_current_balance_to_base(
                    amount=commission,
                    currency=currency,
                )
            )

    dividends = (
        db.query(Dividend)
        .join(
            Investment,
            Dividend.investment_id
            == Investment.id,
        )
        .order_by(
            Dividend.payment_date,
            Dividend.id,
        )
        .all()
    )

    for dividend in dividends:
        investment = (
            dividend.investment
        )

        if investment is None:
            continue

        broker = investment.broker

        currency = normalize_currency(
            dividend.currency
        )

        net_amount = float(
            dividend.net_amount
        )

        add_currency_balance(
            balances=broker_balances[
                broker
            ],
            currency=currency,
            amount=net_amount,
        )

        broker_stats[
            broker
        ]["dividends"] += (
            convert_current_balance_to_base(
                amount=net_amount,
                currency=currency,
            )
        )

    brokers = []

    total_cash_balance = 0.0

    all_brokers = (
        set(broker_balances.keys())
        | set(broker_stats.keys())
    )

    for broker in sorted(
        all_brokers
    ):
        balances = broker_balances[
            broker
        ]

        stats = broker_stats[
            broker
        ]

        currency_balances = []

        broker_cash_balance = 0.0

        for currency in sorted(
            balances.keys()
        ):
            native_balance = (
                balances[currency]
            )

            base_value = (
                convert_current_balance_to_base(
                    amount=native_balance,
                    currency=currency,
                )
            )

            broker_cash_balance += (
                base_value
            )

            currency_balances.append(
                {
                    "currency": currency,
                    "balance": round(
                        native_balance,
                        4,
                    ),
                    "value_base": round(
                        base_value,
                        2,
                    ),
                }
            )

        total_cash_balance += (
            broker_cash_balance
        )

        brokers.append(
            {
                "broker": broker,
                "cash_balance": round(
                    broker_cash_balance,
                    2,
                ),
                "currency_balances": (
                    currency_balances
                ),
                "deposits": round(
                    stats["deposits"],
                    2,
                ),
                "withdrawals": round(
                    stats["withdrawals"],
                    2,
                ),
                "buys": round(
                    stats["buys"],
                    2,
                ),
                "sells": round(
                    stats["sells"],
                    2,
                ),
                "commissions": round(
                    stats["commissions"],
                    2,
                ),
                "dividends": round(
                    stats["dividends"],
                    2,
                ),
                "other_income": round(
                    stats["other_income"],
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    return {
        "cash_balance": round(
            total_cash_balance,
            2,
        ),
        "brokers": brokers,
        "base_currency": BASE_CURRENCY,
    }