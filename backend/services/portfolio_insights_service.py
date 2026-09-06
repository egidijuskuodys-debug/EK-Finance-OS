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


def _make_insight(
    category: str,
    priority: str,
    title: str,
    message: str,
) -> dict:
    return {
        "category": category,
        "priority": priority,
        "title": title,
        "message": message,
    }


def get_portfolio_insights(
    db: Session,
):
    risk = get_portfolio_risk(
        db
    )

    health = get_portfolio_health(
        db
    )

    performance = (
        get_performance_breakdown(
            db
        )
    )

    insights = []

    health_score = float(
        health["score"]
    )

    health_label = (
        health["label"]
    )

    insights.append(
        _make_insight(
            category="Health",
            priority="Info",
            title=(
                "Portfolio health score"
            ),
            message=(
                f"Portfolio health is "
                f"{health_score:.0f}/"
                f"{health['max_score']} "
                f"({health_label})."
            ),
        )
    )

    largest_position = (
        risk["largest_position"]
    )

    if largest_position is not None:
        percentage = float(
            largest_position[
                "percentage"
            ]
        )

        if percentage >= 20:
            priority = "High"
        elif percentage >= 10:
            priority = "Medium"
        else:
            priority = "Low"

        insights.append(
            _make_insight(
                category="Concentration",
                priority=priority,
                title=(
                    "Largest position"
                ),
                message=(
                    f"{largest_position['ticker']} "
                    f"represents "
                    f"{percentage:.2f}% "
                    "of portfolio value."
                ),
            )
        )

    largest_broker = (
        risk["largest_broker"]
    )

    if largest_broker is not None:
        percentage = float(
            largest_broker[
                "percentage"
            ]
        )

        if percentage >= 60:
            priority = "High"
        elif percentage >= 40:
            priority = "Medium"
        else:
            priority = "Low"

        insights.append(
            _make_insight(
                category="Broker",
                priority=priority,
                title=(
                    "Broker concentration"
                ),
                message=(
                    f"{largest_broker['broker']} "
                    f"holds "
                    f"{percentage:.2f}% "
                    "of portfolio value."
                ),
            )
        )

    largest_currency = (
        risk["largest_currency"]
    )

    if largest_currency is not None:
        percentage = float(
            largest_currency[
                "percentage"
            ]
        )

        if percentage >= 70:
            priority = "High"
        elif percentage >= 50:
            priority = "Medium"
        else:
            priority = "Low"

        insights.append(
            _make_insight(
                category="Currency",
                priority=priority,
                title=(
                    "Currency exposure"
                ),
                message=(
                    f"{largest_currency['currency']} "
                    f"represents "
                    f"{percentage:.2f}% "
                    "of portfolio value."
                ),
            )
        )

    summary = (
        performance["summary"]
    )

    unrealized_profit = float(
        summary[
            "unrealized_profit"
        ]
    )

    unrealized_return = float(
        summary[
            "unrealized_return_percent"
        ]
    )

    realized_profit = float(
        summary[
            "realized_profit"
        ]
    )

    dividends = float(
        summary[
            "dividend_net"
        ]
    )

    total_profit = float(
        summary[
            "total_profit"
        ]
    )

    insights.append(
        _make_insight(
            category="Performance",
            priority="Info",
            title=(
                "Current unrealized result"
            ),
            message=(
                f"Open positions show "
                f"{unrealized_profit:.2f} EUR "
                f"of unrealized P/L "
                f"({unrealized_return:.2f}%)."
            ),
        )
    )

    insights.append(
        _make_insight(
            category="Performance",
            priority="Info",
            title=(
                "Realized result"
            ),
            message=(
                f"Realized P/L is "
                f"{realized_profit:.2f} EUR."
            ),
        )
    )

    if dividends > 0:
        insights.append(
            _make_insight(
                category="Income",
                priority="Info",
                title=(
                    "Dividend income"
                ),
                message=(
                    f"Net dividends total "
                    f"{dividends:.2f} EUR."
                ),
            )
        )

    insights.append(
        _make_insight(
            category="Performance",
            priority="Info",
            title=(
                "Total investment result"
            ),
            message=(
                f"Combined unrealized, "
                f"realized and dividend "
                f"result is "
                f"{total_profit:.2f} EUR."
            ),
        )
    )

    best_position = (
        performance[
            "best_position"
        ]
    )

    if best_position is not None:
        insights.append(
            _make_insight(
                category="Performance",
                priority="Info",
                title=(
                    "Best contributor"
                ),
                message=(
                    f"{best_position['ticker']} "
                    f"is currently the strongest "
                    f"contributor with "
                    f"{best_position['total_profit']:.2f} "
                    "EUR total P/L."
                ),
            )
        )

    worst_position = (
        performance[
            "worst_position"
        ]
    )

    if worst_position is not None:
        worst_profit = float(
            worst_position[
                "total_profit"
            ]
        )

        priority = (
            "Medium"
            if worst_profit < 0
            else "Info"
        )

        insights.append(
            _make_insight(
                category="Performance",
                priority=priority,
                title=(
                    "Weakest contributor"
                ),
                message=(
                    f"{worst_position['ticker']} "
                    f"is currently the weakest "
                    f"contributor with "
                    f"{worst_profit:.2f} "
                    "EUR total P/L."
                ),
            )
        )

    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
        "Info": 3,
    }

    insights.sort(
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
        for item in insights
        if item["priority"] == "High"
    )

    medium_priority_count = sum(
        1
        for item in insights
        if item["priority"] == "Medium"
    )

    return {
        "summary": {
            "health_score": (
                health_score
            ),
            "health_label": (
                health_label
            ),
            "insights_count": len(
                insights
            ),
            "high_priority_count": (
                high_priority_count
            ),
            "medium_priority_count": (
                medium_priority_count
            ),
        },
        "insights": insights,
    }