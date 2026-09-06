from sqlalchemy.orm import Session

from services.performance_breakdown_service import (
    get_performance_breakdown,
)
from services.portfolio_health_service import (
    get_portfolio_health,
)
from services.risk_service import (
    get_portfolio_risk,
)


def _make_action(
    category: str,
    priority: str,
    action_type: str,
    title: str,
    message: str,
    reason: str,
) -> dict:
    return {
        "category": category,
        "priority": priority,
        "action_type": action_type,
        "title": title,
        "message": message,
        "reason": reason,
    }


def _get_priority_from_level(
    level: str,
) -> str:
    if level == "High":
        return "High"

    if level == "Moderate":
        return "Medium"

    return "Low"


def get_portfolio_actions(
    db: Session,
):
    health = get_portfolio_health(
        db
    )

    risk = get_portfolio_risk(
        db
    )

    performance = (
        get_performance_breakdown(
            db
        )
    )

    actions = []

    assessment = (
        risk[
            "risk_assessment"
        ]
    )

    health_score = float(
        health["score"]
    )

    health_label = (
        health["label"]
    )

    if health_score >= 85:
        actions.append(
            _make_action(
                category="Health",
                priority="Low",
                action_type="Maintain",
                title=(
                    "Maintain portfolio structure"
                ),
                message=(
                    "No major structural changes "
                    "are indicated by the current "
                    "health score."
                ),
                reason=(
                    f"Portfolio health is "
                    f"{health_score:.0f}/"
                    f"{health['max_score']} "
                    f"({health_label})."
                ),
            )
        )

    elif health_score >= 70:
        actions.append(
            _make_action(
                category="Health",
                priority="Medium",
                action_type="Monitor",
                title=(
                    "Improve weaker diversification areas"
                ),
                message=(
                    "Maintain the overall portfolio "
                    "structure while monitoring the "
                    "weaker diversification components."
                ),
                reason=(
                    f"Portfolio health is "
                    f"{health_score:.0f}/"
                    f"{health['max_score']} "
                    f"({health_label})."
                ),
            )
        )

    else:
        actions.append(
            _make_action(
                category="Health",
                priority="High",
                action_type="Review",
                title=(
                    "Review portfolio structure"
                ),
                message=(
                    "Review the main concentration "
                    "drivers before increasing existing "
                    "portfolio exposures."
                ),
                reason=(
                    f"Portfolio health is "
                    f"{health_score:.0f}/"
                    f"{health['max_score']} "
                    f"({health_label})."
                ),
            )
        )

    position_assessment = (
        assessment[
            "position_concentration"
        ]
    )

    position_level = (
        position_assessment[
            "level"
        ]
    )

    position_percentage = float(
        position_assessment[
            "percentage"
        ]
    )

    largest_position = (
        risk[
            "largest_position"
        ]
    )

    if (
        largest_position is not None
        and position_level != "Low"
    ):
        actions.append(
            _make_action(
                category="Concentration",
                priority=(
                    _get_priority_from_level(
                        position_level
                    )
                ),
                action_type="Monitor",
                title=(
                    "Monitor largest position"
                ),
                message=(
                    "Avoid increasing the largest "
                    "position without first checking "
                    "its effect on portfolio "
                    "concentration."
                ),
                reason=(
                    f"{largest_position['ticker']} "
                    f"currently represents "
                    f"{position_percentage:.2f}% "
                    "of portfolio value."
                ),
            )
        )

    broker_assessment = (
        assessment[
            "broker_concentration"
        ]
    )

    broker_level = (
        broker_assessment[
            "level"
        ]
    )

    broker = (
        broker_assessment[
            "broker"
        ]
    )

    broker_percentage = float(
        broker_assessment[
            "percentage"
        ]
    )

    if (
        broker is not None
        and broker_level != "Low"
    ):
        actions.append(
            _make_action(
                category="Broker",
                priority=(
                    _get_priority_from_level(
                        broker_level
                    )
                ),
                action_type="Consider",
                title=(
                    "Consider broker diversification"
                ),
                message=(
                    "When making future contributions, "
                    "consider whether directing some "
                    "new capital through other brokers "
                    "would reduce operational "
                    "concentration."
                ),
                reason=(
                    f"{broker} currently holds "
                    f"{broker_percentage:.2f}% "
                    "of portfolio value."
                ),
            )
        )

    currency_assessment = (
        assessment[
            "currency_concentration"
        ]
    )

    currency_level = (
        currency_assessment[
            "level"
        ]
    )

    currency = (
        currency_assessment[
            "currency"
        ]
    )

    currency_percentage = float(
        currency_assessment[
            "percentage"
        ]
    )

    if (
        currency is not None
        and currency_level != "Low"
    ):
        actions.append(
            _make_action(
                category="Currency",
                priority=(
                    _get_priority_from_level(
                        currency_level
                    )
                ),
                action_type="Monitor",
                title=(
                    "Monitor currency exposure"
                ),
                message=(
                    "Review how future investments "
                    "affect the portfolio currency mix "
                    "before adding more exposure to the "
                    "largest currency."
                ),
                reason=(
                    f"{currency} currently represents "
                    f"{currency_percentage:.2f}% "
                    "of portfolio value."
                ),
            )
        )

    hhi_assessment = (
        assessment[
            "hhi_concentration"
        ]
    )

    if (
        hhi_assessment[
            "level"
        ]
        == "Low"
    ):
        actions.append(
            _make_action(
                category="Diversification",
                priority="Low",
                action_type="Maintain",
                title=(
                    "Maintain position diversification"
                ),
                message=(
                    "Current overall position "
                    "diversification does not require "
                    "corrective action."
                ),
                reason=(
                    f"Portfolio HHI is "
                    f"{hhi_assessment['value']:.2f} "
                    "and is classified as Low."
                ),
            )
        )

    worst_position = (
        performance[
            "worst_position"
        ]
    )

    if (
        worst_position is not None
        and float(
            worst_position[
                "total_profit"
            ]
        ) < 0
    ):
        actions.append(
            _make_action(
                category="Performance",
                priority="Medium",
                action_type="Review",
                title=(
                    "Review weakest contributor"
                ),
                message=(
                    "Review the investment thesis, "
                    "position size and risk of the "
                    "weakest contributor. A negative "
                    "result alone is not treated as an "
                    "automatic sell signal."
                ),
                reason=(
                    f"{worst_position['ticker']} "
                    f"currently has "
                    f"{worst_position['total_profit']:.2f} "
                    "EUR total P/L."
                ),
            )
        )

    best_position = (
        performance[
            "best_position"
        ]
    )

    if best_position is not None:
        actions.append(
            _make_action(
                category="Performance",
                priority="Low",
                action_type="Monitor",
                title=(
                    "Monitor strongest contributor"
                ),
                message=(
                    "Monitor whether strong performance "
                    "causes the position to become too "
                    "large relative to the portfolio."
                ),
                reason=(
                    f"{best_position['ticker']} "
                    f"currently contributes "
                    f"{best_position['total_profit']:.2f} "
                    "EUR total P/L."
                ),
            )
        )

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    actions.sort(
        key=lambda item: (
            priority_order.get(
                item["priority"],
                99,
            ),
            item["category"],
            item["title"],
        )
    )

    high_priority_count = sum(
        1
        for action in actions
        if action["priority"] == "High"
    )

    medium_priority_count = sum(
        1
        for action in actions
        if action["priority"] == "Medium"
    )

    low_priority_count = sum(
        1
        for action in actions
        if action["priority"] == "Low"
    )

    return {
        "summary": {
            "health_score": round(
                health_score,
                2,
            ),
            "health_label": (
                health_label
            ),
            "actions_count": len(
                actions
            ),
            "high_priority_count": (
                high_priority_count
            ),
            "medium_priority_count": (
                medium_priority_count
            ),
            "low_priority_count": (
                low_priority_count
            ),
        },
        "actions": actions,
    }