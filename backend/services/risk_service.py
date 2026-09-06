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


def _get_hhi_level(
    hhi: float,
) -> str:
    if hhi < 1000:
        return "Low"

    if hhi < 1800:
        return "Moderate"

    return "High"


def _get_position_level(
    percentage: float,
) -> str:
    if percentage < 10:
        return "Low"

    if percentage < 20:
        return "Moderate"

    return "High"


def _get_broker_level(
    percentage: float,
) -> str:
    if percentage < 40:
        return "Low"

    if percentage < 60:
        return "Moderate"

    return "High"


def _get_currency_level(
    percentage: float,
) -> str:
    if percentage < 50:
        return "Low"

    if percentage < 70:
        return "Moderate"

    return "High"


def _risk_score(
    level: str,
) -> int:
    scores = {
        "Low": 1,
        "Moderate": 2,
        "High": 3,
    }

    return scores[level]


def _get_overall_level(
    levels: list[str],
) -> str:
    if not levels:
        return "Low"

    highest_score = max(
        _risk_score(level)
        for level in levels
    )

    if highest_score == 3:
        return "High"

    if highest_score == 2:
        return "Moderate"

    return "Low"


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

    position_level = (
        _get_position_level(
            top_1_percentage
        )
    )

    hhi_level = (
        _get_hhi_level(
            concentration_hhi
        )
    )

    broker_level = (
        _get_broker_level(
            largest_broker[
                "percentage"
            ]
        )
        if largest_broker
        else "Low"
    )

    currency_level = (
        _get_currency_level(
            largest_currency[
                "percentage"
            ]
        )
        if largest_currency
        else "Low"
    )

    overall_level = (
        _get_overall_level(
            [
                position_level,
                hhi_level,
                broker_level,
                currency_level,
            ]
        )
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
        "risk_assessment": {
            "overall_level": (
                overall_level
            ),
            "position_concentration": {
                "level": (
                    position_level
                ),
                "percentage": round(
                    top_1_percentage,
                    2,
                ),
            },
            "hhi_concentration": {
                "level": hhi_level,
                "value": round(
                    concentration_hhi,
                    2,
                ),
            },
            "broker_concentration": {
                "level": (
                    broker_level
                ),
                "percentage": (
                    largest_broker[
                        "percentage"
                    ]
                    if largest_broker
                    else 0.0
                ),
                "broker": (
                    largest_broker[
                        "broker"
                    ]
                    if largest_broker
                    else None
                ),
            },
            "currency_concentration": {
                "level": (
                    currency_level
                ),
                "percentage": (
                    largest_currency[
                        "percentage"
                    ]
                    if largest_currency
                    else 0.0
                ),
                "currency": (
                    largest_currency[
                        "currency"
                    ]
                    if largest_currency
                    else None
                ),
            },
        },
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