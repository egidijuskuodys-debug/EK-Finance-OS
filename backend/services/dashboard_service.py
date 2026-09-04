from sqlalchemy.orm import Session

from repositories import dashboard_repository
from services.analytics_service import (
    get_allocation,
    get_performance,
    get_summary,
)
from services.performance_service import (
    get_portfolio_xirr,
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

    performance_summary = (
        get_portfolio_xirr(
            db
        )
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
        "portfolio_value": (
            performance_summary[
                "total_wealth"
            ]
        ),
        "total_invested": summary[
            "total_invested"
        ],
        "securities_value": (
            performance_summary[
                "securities_value"
            ]
        ),
        "cash_balance": (
            performance_summary[
                "cash_balance"
            ]
        ),
        "total_wealth": (
            performance_summary[
                "total_wealth"
            ]
        ),
        "total_deposits": (
            performance_summary[
                "total_deposits"
            ]
        ),
        "total_withdrawals": (
            performance_summary[
                "total_withdrawals"
            ]
        ),
        "net_contributions": (
            performance_summary[
                "net_contributions"
            ]
        ),
        "investment_gain": (
            performance_summary[
                "investment_gain"
            ]
        ),
        "investment_gain_percent": (
            performance_summary[
                "investment_gain_percent"
            ]
        ),
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
        "xirr": performance_summary[
            "xirr"
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