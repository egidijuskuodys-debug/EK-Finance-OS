from sqlalchemy.orm import Session

from repositories import dashboard_repository
from services.analytics_service import (
    get_allocation,
    get_performance,
    get_summary,
)


def get_dashboard(
    db: Session,
):
    summary = get_summary(
        db
    )

    allocation = get_allocation(
        db
    )

    performance = get_performance(
        db
    )

    total_quantity = (
        dashboard_repository
        .get_total_quantity(
            db
        )
    )

    asset_allocation = []

    for item in allocation[
        "by_asset_type"
    ]:
        asset_allocation.append(
            {
                "name": item[
                    "asset_type"
                ],
                "value": item[
                    "value"
                ],
                "percentage": item[
                    "percentage"
                ],
            }
        )

    sorted_positions = sorted(
        performance,
        key=lambda item: (
            item[
                "base_current_value"
            ]
        ),
        reverse=True,
    )

    top_positions = []

    for item in sorted_positions[:5]:
        top_positions.append(
            {
                "ticker": item[
                    "ticker"
                ],
                "asset_type": item[
                    "asset_type"
                ],
                "current_value": item[
                    "base_current_value"
                ],
                "profit_loss": item[
                    "base_profit_loss"
                ],
                "profit_loss_percent": item[
                    "profit_loss_percent"
                ],
            }
        )

    return {
        "total_positions": summary[
            "positions"
        ],
        "total_quantity": round(
            total_quantity,
            8,
        ),
        "portfolio_value": summary[
            "portfolio_value"
        ],
        "total_invested": summary[
            "total_invested"
        ],
        "unrealized_profit": summary[
            "unrealized_profit"
        ],
        "unrealized_profit_percent": (
            summary[
                "unrealized_profit_percent"
            ]
        ),
        "realized_profit": summary[
            "realized_profit"
        ],
        "dividend_net": summary[
            "dividend_net"
        ],
        "total_profit": summary[
            "total_profit"
        ],
        "total_return_percent": summary[
            "total_return_percent"
        ],
        "best_position": summary[
            "best_position"
        ],
        "worst_position": summary[
            "worst_position"
        ],
        "base_currency": summary[
            "base_currency"
        ],
        "asset_allocation": (
            asset_allocation
        ),
        "top_positions": (
            top_positions
        ),
    }