from collections import defaultdict

from sqlalchemy.orm import Session

from models.dividend import Dividend
from models.investment import Investment
from models.transaction import Transaction
from services.analytics_service import (
    convert_dividend_to_base,
)
from services.fx_service import (
    BASE_CURRENCY,
    convert_to_base_currency,
)


def _convert_realized_profit_to_base(
    amount: float,
    currency: str,
    fx_rate: float | None,
) -> float:
    currency = (
        currency
        .strip()
        .upper()
    )

    amount = float(
        amount
    )

    if currency == BASE_CURRENCY:
        return amount

    if (
        fx_rate is not None
        and float(fx_rate) > 0
    ):
        return (
            amount
            / float(fx_rate)
        )

    return convert_to_base_currency(
        amount=amount,
        currency=currency,
    )


def _new_group() -> dict:
    return {
        "open_cost_basis": 0.0,
        "current_value": 0.0,
        "unrealized_profit": 0.0,
        "realized_profit": 0.0,
        "dividend_net": 0.0,
        "total_profit": 0.0,
        "positions": 0,
        "open_positions": 0,
    }


def get_performance_breakdown(
    db: Session,
):
    investments = (
        db.query(
            Investment
        )
        .all()
    )

    transactions = (
        db.query(
            Transaction
        )
        .all()
    )

    dividends = (
        db.query(
            Dividend
        )
        .all()
    )

    realized_by_investment = (
        defaultdict(float)
    )

    dividend_by_investment = (
        defaultdict(float)
    )

    for transaction in transactions:
        realized_profit = float(
            transaction.realized_profit
            or 0.0
        )

        if realized_profit == 0:
            continue

        realized_by_investment[
            transaction.investment_id
        ] += (
            _convert_realized_profit_to_base(
                amount=realized_profit,
                currency=(
                    transaction.currency
                    or BASE_CURRENCY
                ),
                fx_rate=(
                    transaction.fx_rate
                ),
            )
        )

    for dividend in dividends:
        dividend_by_investment[
            dividend.investment_id
        ] += (
            convert_dividend_to_base(
                amount=dividend.net_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

    positions = []

    broker_data = defaultdict(
        _new_group
    )

    asset_type_data = defaultdict(
        _new_group
    )

    total_open_cost_basis = 0.0
    total_current_value = 0.0
    total_unrealized_profit = 0.0
    total_realized_profit = 0.0
    total_dividend_net = 0.0

    open_positions = 0
    closed_positions = 0

    for investment in investments:
        quantity = float(
            investment.quantity
            or 0.0
        )

        purchase_price = float(
            investment.purchase_price
            or 0.0
        )

        current_price = float(
            investment.current_price
            or 0.0
        )

        local_cost_basis = (
            quantity
            * purchase_price
        )

        local_current_value = (
            quantity
            * current_price
        )

        open_cost_basis = (
            convert_to_base_currency(
                amount=local_cost_basis,
                currency=investment.currency,
            )
            if local_cost_basis != 0
            else 0.0
        )

        current_value = (
            convert_to_base_currency(
                amount=local_current_value,
                currency=investment.currency,
            )
            if local_current_value != 0
            else 0.0
        )

        unrealized_profit = (
            current_value
            - open_cost_basis
        )

        realized_profit = (
            realized_by_investment[
                investment.id
            ]
        )

        dividend_net = (
            dividend_by_investment[
                investment.id
            ]
        )

        total_profit = (
            unrealized_profit
            + realized_profit
            + dividend_net
        )

        if open_cost_basis > 0:
            unrealized_return_percent = (
                unrealized_profit
                / open_cost_basis
            ) * 100
        else:
            unrealized_return_percent = 0.0

        is_open = (
            quantity > 0
        )

        if is_open:
            open_positions += 1
            status = "OPEN"
        else:
            closed_positions += 1
            status = "CLOSED"

        position = {
            "investment_id": (
                investment.id
            ),
            "broker": (
                investment.broker
            ),
            "ticker": (
                investment.ticker
            ),
            "asset": (
                investment.asset
            ),
            "asset_type": (
                investment.asset_type
            ),
            "status": status,
            "quantity": round(
                quantity,
                8,
            ),
            "currency": (
                investment.currency
            ),
            "open_cost_basis": round(
                open_cost_basis,
                2,
            ),
            "current_value": round(
                current_value,
                2,
            ),
            "unrealized_profit": round(
                unrealized_profit,
                2,
            ),
            "unrealized_return_percent": (
                round(
                    unrealized_return_percent,
                    2,
                )
            ),
            "realized_profit": round(
                realized_profit,
                2,
            ),
            "dividend_net": round(
                dividend_net,
                2,
            ),
            "total_profit": round(
                total_profit,
                2,
            ),
            "base_currency": (
                BASE_CURRENCY
            ),
        }

        positions.append(
            position
        )

        for group in (
            broker_data[
                investment.broker
            ],
            asset_type_data[
                investment.asset_type
            ],
        ):
            group[
                "open_cost_basis"
            ] += open_cost_basis

            group[
                "current_value"
            ] += current_value

            group[
                "unrealized_profit"
            ] += unrealized_profit

            group[
                "realized_profit"
            ] += realized_profit

            group[
                "dividend_net"
            ] += dividend_net

            group[
                "total_profit"
            ] += total_profit

            group[
                "positions"
            ] += 1

            if is_open:
                group[
                    "open_positions"
                ] += 1

        total_open_cost_basis += (
            open_cost_basis
        )

        total_current_value += (
            current_value
        )

        total_unrealized_profit += (
            unrealized_profit
        )

        total_realized_profit += (
            realized_profit
        )

        total_dividend_net += (
            dividend_net
        )

    positions.sort(
        key=lambda item: (
            item["total_profit"]
        ),
        reverse=True,
    )

    total_profit = (
        total_unrealized_profit
        + total_realized_profit
        + total_dividend_net
    )

    if total_open_cost_basis > 0:
        unrealized_return_percent = (
            total_unrealized_profit
            / total_open_cost_basis
        ) * 100
    else:
        unrealized_return_percent = 0.0

    def build_group_result(
        data: dict,
        name_key: str,
    ) -> list[dict]:
        result = []

        for name, values in data.items():
            result.append(
                {
                    name_key: name,
                    "open_cost_basis": round(
                        values[
                            "open_cost_basis"
                        ],
                        2,
                    ),
                    "current_value": round(
                        values[
                            "current_value"
                        ],
                        2,
                    ),
                    "unrealized_profit": round(
                        values[
                            "unrealized_profit"
                        ],
                        2,
                    ),
                    "realized_profit": round(
                        values[
                            "realized_profit"
                        ],
                        2,
                    ),
                    "dividend_net": round(
                        values[
                            "dividend_net"
                        ],
                        2,
                    ),
                    "total_profit": round(
                        values[
                            "total_profit"
                        ],
                        2,
                    ),
                    "positions": (
                        values[
                            "positions"
                        ]
                    ),
                    "open_positions": (
                        values[
                            "open_positions"
                        ]
                    ),
                    "base_currency": (
                        BASE_CURRENCY
                    ),
                }
            )

        result.sort(
            key=lambda item: (
                item["total_profit"]
            ),
            reverse=True,
        )

        return result

    by_broker = build_group_result(
        broker_data,
        "broker",
    )

    by_asset_type = (
        build_group_result(
            asset_type_data,
            "asset_type",
        )
    )

    best_position = (
        positions[0]
        if positions
        else None
    )

    worst_position = (
        positions[-1]
        if positions
        else None
    )

    return {
        "summary": {
            "open_cost_basis": round(
                total_open_cost_basis,
                2,
            ),
            "current_value": round(
                total_current_value,
                2,
            ),
            "unrealized_profit": round(
                total_unrealized_profit,
                2,
            ),
            "unrealized_return_percent": (
                round(
                    unrealized_return_percent,
                    2,
                )
            ),
            "realized_profit": round(
                total_realized_profit,
                2,
            ),
            "dividend_net": round(
                total_dividend_net,
                2,
            ),
            "total_profit": round(
                total_profit,
                2,
            ),
            "positions": len(
                positions
            ),
            "open_positions": (
                open_positions
            ),
            "closed_positions": (
                closed_positions
            ),
            "base_currency": (
                BASE_CURRENCY
            ),
        },
        "best_position": (
            best_position
        ),
        "worst_position": (
            worst_position
        ),
        "positions": (
            positions
        ),
        "by_broker": (
            by_broker
        ),
        "by_asset_type": (
            by_asset_type
        ),
    }