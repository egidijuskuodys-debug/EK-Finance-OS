from sqlalchemy.orm import Session

from services.risk_service import (
    get_portfolio_risk,
)


MAX_SCORE = 100

POSITION_WEIGHT = 30
HHI_WEIGHT = 25
BROKER_WEIGHT = 20
CURRENCY_WEIGHT = 15
ASSET_TYPE_WEIGHT = 10


def _score_level(
    level: str,
    weight: int,
) -> float:
    if level == "Low":
        return float(
            weight
        )

    if level == "Moderate":
        return float(
            weight
            * 0.6
        )

    if level == "High":
        return float(
            weight
            * 0.2
        )

    return 0.0


def _score_asset_type_diversification(
    asset_types: list[dict],
) -> float:
    if not asset_types:
        return 0.0

    active_types = [
        item
        for item in asset_types
        if item.get(
            "percentage",
            0.0,
        ) > 0
    ]

    count = len(
        active_types
    )

    if count >= 3:
        return float(
            ASSET_TYPE_WEIGHT
        )

    if count == 2:
        return float(
            ASSET_TYPE_WEIGHT
            * 0.7
        )

    if count == 1:
        return float(
            ASSET_TYPE_WEIGHT
            * 0.3
        )

    return 0.0


def _get_health_label(
    score: float,
) -> str:
    if score >= 85:
        return "Excellent"

    if score >= 70:
        return "Good"

    if score >= 50:
        return "Fair"

    return "Weak"


def get_portfolio_health(
    db: Session,
):
    risk = get_portfolio_risk(
        db
    )

    assessment = (
        risk[
            "risk_assessment"
        ]
    )

    position_score = (
        _score_level(
            assessment[
                "position_concentration"
            ][
                "level"
            ],
            POSITION_WEIGHT,
        )
    )

    hhi_score = (
        _score_level(
            assessment[
                "hhi_concentration"
            ][
                "level"
            ],
            HHI_WEIGHT,
        )
    )

    broker_score = (
        _score_level(
            assessment[
                "broker_concentration"
            ][
                "level"
            ],
            BROKER_WEIGHT,
        )
    )

    currency_score = (
        _score_level(
            assessment[
                "currency_concentration"
            ][
                "level"
            ],
            CURRENCY_WEIGHT,
        )
    )

    asset_type_score = (
        _score_asset_type_diversification(
            risk[
                "by_asset_type"
            ]
        )
    )

    total_score = (
        position_score
        + hhi_score
        + broker_score
        + currency_score
        + asset_type_score
    )

    total_score = min(
        float(MAX_SCORE),
        total_score,
    )

    label = (
        _get_health_label(
            total_score
        )
    )

    strengths = []
    watch_items = []

    if (
        assessment[
            "hhi_concentration"
        ][
            "level"
        ]
        == "Low"
    ):
        strengths.append(
            "Overall position concentration "
            "is well diversified."
        )
    else:
        watch_items.append(
            "Portfolio concentration "
            "should be monitored."
        )

    if (
        assessment[
            "broker_concentration"
        ][
            "level"
        ]
        == "Low"
    ):
        strengths.append(
            "Broker exposure is diversified."
        )
    else:
        broker = (
            assessment[
                "broker_concentration"
            ][
                "broker"
            ]
        )

        percentage = (
            assessment[
                "broker_concentration"
            ][
                "percentage"
            ]
        )

        watch_items.append(
            f"{broker} represents "
            f"{percentage:.2f}% "
            "of portfolio value."
        )

    if (
        assessment[
            "currency_concentration"
        ][
            "level"
        ]
        == "Low"
    ):
        strengths.append(
            "Currency exposure is diversified."
        )
    else:
        currency = (
            assessment[
                "currency_concentration"
            ][
                "currency"
            ]
        )

        percentage = (
            assessment[
                "currency_concentration"
            ][
                "percentage"
            ]
        )

        watch_items.append(
            f"{currency} represents "
            f"{percentage:.2f}% "
            "of portfolio value."
        )

    if (
        assessment[
            "position_concentration"
        ][
            "level"
        ]
        == "Low"
    ):
        strengths.append(
            "No single position dominates "
            "the portfolio."
        )
    else:
        percentage = (
            assessment[
                "position_concentration"
            ][
                "percentage"
            ]
        )

        watch_items.append(
            "Largest position represents "
            f"{percentage:.2f}% "
            "of portfolio value."
        )

    if asset_type_score == ASSET_TYPE_WEIGHT:
        strengths.append(
            "Portfolio includes multiple "
            "asset types."
        )
    else:
        watch_items.append(
            "Asset type diversification "
            "is limited."
        )

    return {
        "score": round(
            total_score,
            2,
        ),
        "max_score": (
            MAX_SCORE
        ),
        "label": label,
        "components": {
            "position_diversification": {
                "score": round(
                    position_score,
                    2,
                ),
                "max_score": (
                    POSITION_WEIGHT
                ),
            },
            "hhi_diversification": {
                "score": round(
                    hhi_score,
                    2,
                ),
                "max_score": (
                    HHI_WEIGHT
                ),
            },
            "broker_diversification": {
                "score": round(
                    broker_score,
                    2,
                ),
                "max_score": (
                    BROKER_WEIGHT
                ),
            },
            "currency_diversification": {
                "score": round(
                    currency_score,
                    2,
                ),
                "max_score": (
                    CURRENCY_WEIGHT
                ),
            },
            "asset_type_diversification": {
                "score": round(
                    asset_type_score,
                    2,
                ),
                "max_score": (
                    ASSET_TYPE_WEIGHT
                ),
            },
        },
        "strengths": strengths,
        "watch_items": (
            watch_items
        ),
        "base_currency": (
            risk[
                "base_currency"
            ]
        ),
        "portfolio_value": (
            risk[
                "portfolio_value"
            ]
        ),
    }