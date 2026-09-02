from collections import defaultdict

from sqlalchemy.orm import Session

from repositories import cash_movement_repository
from services.fx_service import (
    BASE_CURRENCY,
    convert_to_base_currency,
)


DEPOSIT_TYPES = {
    "DEPOSIT",
    "CASH TOP-UP",
}

WITHDRAWAL_TYPES = {
    "WITHDRAWAL",
    "CASH WITHDRAWAL",
}


def convert_cash_movement_to_base(
    amount: float,
    currency: str,
    fx_rate: float | None,
) -> float:
    currency = (
        currency
        .strip()
        .upper()
    )

    if currency == BASE_CURRENCY:
        return float(amount)

    if (
        fx_rate is not None
        and float(fx_rate) > 0
    ):
        return (
            float(amount)
            / float(fx_rate)
        )

    return convert_to_base_currency(
        amount=float(amount),
        currency=currency,
    )


def normalize_movement_type(
    movement_type: str,
) -> str:
    return (
        movement_type
        .strip()
        .upper()
    )


def get_cash_flow_summary(
    db: Session,
):
    movements = (
        cash_movement_repository
        .get_all(
            db
        )
    )

    total_deposits = 0.0
    total_withdrawals = 0.0

    deposits_count = 0
    withdrawals_count = 0

    for movement in movements:
        movement_type = (
            normalize_movement_type(
                movement.movement_type
            )
        )

        amount_base = (
            convert_cash_movement_to_base(
                amount=movement.amount,
                currency=movement.currency,
                fx_rate=movement.fx_rate,
            )
        )

        if movement_type in DEPOSIT_TYPES:
            total_deposits += abs(
                amount_base
            )

            deposits_count += 1

        elif (
            movement_type
            in WITHDRAWAL_TYPES
        ):
            total_withdrawals += abs(
                amount_base
            )

            withdrawals_count += 1

    net_contributions = (
        total_deposits
        - total_withdrawals
    )

    return {
        "total_deposits": round(
            total_deposits,
            2,
        ),
        "total_withdrawals": round(
            total_withdrawals,
            2,
        ),
        "net_contributions": round(
            net_contributions,
            2,
        ),
        "deposits_count": (
            deposits_count
        ),
        "withdrawals_count": (
            withdrawals_count
        ),
        "base_currency": (
            BASE_CURRENCY
        ),
    }


def get_cash_flow_by_broker(
    db: Session,
):
    movements = (
        cash_movement_repository
        .get_all(
            db
        )
    )

    broker_data = defaultdict(
        lambda: {
            "deposits": 0.0,
            "withdrawals": 0.0,
            "deposits_count": 0,
            "withdrawals_count": 0,
        }
    )

    for movement in movements:
        movement_type = (
            normalize_movement_type(
                movement.movement_type
            )
        )

        amount_base = (
            convert_cash_movement_to_base(
                amount=movement.amount,
                currency=movement.currency,
                fx_rate=movement.fx_rate,
            )
        )

        data = broker_data[
            movement.broker
        ]

        if movement_type in DEPOSIT_TYPES:
            data["deposits"] += abs(
                amount_base
            )

            data[
                "deposits_count"
            ] += 1

        elif (
            movement_type
            in WITHDRAWAL_TYPES
        ):
            data[
                "withdrawals"
            ] += abs(
                amount_base
            )

            data[
                "withdrawals_count"
            ] += 1

    result = []

    for broker in sorted(
        broker_data.keys()
    ):
        data = broker_data[
            broker
        ]

        net_contributions = (
            data["deposits"]
            - data["withdrawals"]
        )

        result.append(
            {
                "broker": broker,
                "deposits": round(
                    data["deposits"],
                    2,
                ),
                "withdrawals": round(
                    data["withdrawals"],
                    2,
                ),
                "net_contributions": round(
                    net_contributions,
                    2,
                ),
                "deposits_count": (
                    data[
                        "deposits_count"
                    ]
                ),
                "withdrawals_count": (
                    data[
                        "withdrawals_count"
                    ]
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    return result


def get_cash_flow_by_year(
    db: Session,
):
    movements = (
        cash_movement_repository
        .get_all(
            db
        )
    )

    yearly_data = defaultdict(
        lambda: {
            "deposits": 0.0,
            "withdrawals": 0.0,
            "deposits_count": 0,
            "withdrawals_count": 0,
        }
    )

    for movement in movements:
        movement_type = (
            normalize_movement_type(
                movement.movement_type
            )
        )

        amount_base = (
            convert_cash_movement_to_base(
                amount=movement.amount,
                currency=movement.currency,
                fx_rate=movement.fx_rate,
            )
        )

        year = (
            movement.movement_date.year
        )

        data = yearly_data[
            year
        ]

        if movement_type in DEPOSIT_TYPES:
            data["deposits"] += abs(
                amount_base
            )

            data[
                "deposits_count"
            ] += 1

        elif (
            movement_type
            in WITHDRAWAL_TYPES
        ):
            data[
                "withdrawals"
            ] += abs(
                amount_base
            )

            data[
                "withdrawals_count"
            ] += 1

    result = []

    for year in sorted(
        yearly_data.keys(),
        reverse=True,
    ):
        data = yearly_data[
            year
        ]

        net_contributions = (
            data["deposits"]
            - data["withdrawals"]
        )

        result.append(
            {
                "year": year,
                "deposits": round(
                    data["deposits"],
                    2,
                ),
                "withdrawals": round(
                    data["withdrawals"],
                    2,
                ),
                "net_contributions": round(
                    net_contributions,
                    2,
                ),
                "deposits_count": (
                    data[
                        "deposits_count"
                    ]
                ),
                "withdrawals_count": (
                    data[
                        "withdrawals_count"
                    ]
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    return result