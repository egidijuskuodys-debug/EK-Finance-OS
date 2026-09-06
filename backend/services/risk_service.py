from collections import defaultdict

from sqlalchemy.orm import Session

from models.investment import Investment
from services.fx_service import (
    BASE_CURRENCY,
    convert_to_base_currency,
)


def _get_position_value(
    investment: Investment,
) -> float:
    local_value = (
        investment.quantity
        * investment.current_price
    )

    return convert_to_base_currency(
        amount=local_value,
        currency=investment.currency,
    )


def _calculate_percentage(
    value: float,
    total_value: float,
) -> float:
    if total_value <= 0:
        return 0.0

    return (
        value
        / total_value
    ) * 100


def get_portfolio_risk(
    db: Session,
):
    investments = (
        db.query(
            Investment
        )
        .all()
    )

    positions = []

    broker_values = defaultdict(
        float
    )

    asset_type_values = defaultdict(
        float
    )

    currency_values = defaultdict(
        float
    )

    total_value = 0.0

    for investment in investments:
        value = _get_position_value(
            investment
        )

        if value <= 0:
            continue

        total_value += value

        broker_values[
            investment.broker
        ] += value

        asset_type_values[
            investment.asset_type
        ] += value

        currency_values[
            investment.currency
        ] += value

        positions.append(
            {
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
                "currency": (
                    investment.currency
                ),
                "value": value,
            }
        )

    positions.sort(
        key=lambda item: item["value"],
        reverse=True,
    )

    top_positions = []

    for position in positions[:10]:
        top_positions.append(
            {
                **position,
                "value": round(
                    position["value"],
                    2,
                ),
                "percentage": round(
                    _calculate_percentage(
                        position["value"],
                        total_value,
                    ),
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    by_broker = []

    for broker, value in sorted(
        broker_values.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        by_broker.append(
            {
                "broker": broker,
                "value": round(
                    value,
                    2,
                ),
                "percentage": round(
                    _calculate_percentage(
                        value,
                        total_value,
                    ),
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    by_asset_type = []

    for asset_type, value in sorted(
        asset_type_values.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        by_asset_type.append(
            {
                "asset_type": (
                    asset_type
                ),
                "value": round(
                    value,
                    2,
                ),
                "percentage": round(
                    _calculate_percentage(
                        value,
                        total_value,
                    ),
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    by_currency = []

    for currency, value in sorted(
        currency_values.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        by_currency.append(
            {
                "currency": currency,
                "value": round(
                    value,
                    2,
                ),
                "percentage": round(
                    _calculate_percentage(
                        value,
                        total_value,
                    ),
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    position_percentages = [
        _calculate_percentage(
            position["value"],
            total_value,
        )
        for position in positions
    ]

    top_1_percentage = sum(
        position_percentages[:1]
    )

    top_3_percentage = sum(
        position_percentages[:3]
    )

    top_5_percentage = sum(
        position_percentages[:5]
    )

    concentration_hhi = sum(
        percentage ** 2
        for percentage
        in position_percentages
    )

    largest_position = (
        top_positions[0]
        if top_positions
        else None
    )

    largest_broker = (
        by_broker[0]
        if by_broker
        else None
    )

    largest_asset_type = (
        by_asset_type[0]
        if by_asset_type
        else None
    )

    largest_currency = (
        by_currency[0]
        if by_currency
        else None
    )

    return {
        "portfolio_value": round(
            total_value,
            2,
        ),
        "base_currency": (
            BASE_CURRENCY
        ),
        "open_positions": len(
            positions
        ),
        "concentration": {
            "top_1_percentage": round(
                top_1_percentage,
                2,
            ),
            "top_3_percentage": round(
                top_3_percentage,
                2,
            ),
            "top_5_percentage": round(
                top_5_percentage,
                2,
            ),
            "hhi": round(
                concentration_hhi,
                2,
            ),
        },
        "largest_position": (
            largest_position
        ),
        "largest_broker": (
            largest_broker
        ),
        "largest_asset_type": (
            largest_asset_type
        ),
        "largest_currency": (
            largest_currency
        ),
        "top_positions": (
            top_positions
        ),
        "by_broker": (
            by_broker
        ),
        "by_asset_type": (
            by_asset_type
        ),
        "by_currency": (
            by_currency
        ),
    }