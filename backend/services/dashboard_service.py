from sqlalchemy.orm import Session

from repositories import (
    dashboard_repository,
)
from services.analytics_service import (
    get_allocation,
    get_performance,
    get_summary,
)
from services.performance_service import (
    get_portfolio_xirr,
)
from services.real_estate_service import (
    get_real_estate_summary,
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

    real_estate_summary = (
        get_real_estate_summary(
            db
        )
    )

    total_quantity = (
        dashboard_repository
        .get_total_quantity(
            db
        )
    )

    investment_wealth = float(
        performance_summary[
            "total_wealth"
        ]
    )

    real_estate_value = float(
        real_estate_summary[
            "total_current_value"
        ]
    )

    real_estate_loan_balance = float(
        real_estate_summary[
            "total_loan_balance"
        ]
    )

    real_estate_equity = float(
        real_estate_summary[
            "total_equity"
        ]
    )

    monthly_rental_cash_flow = float(
        real_estate_summary[
            "total_monthly_cash_flow"
        ]
    )

    net_worth = (
        investment_wealth
        + real_estate_equity
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
        "portfolio_value": round(
            investment_wealth,
            2,
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
        "total_wealth": round(
            investment_wealth,
            2,
        ),
        "real_estate_value": round(
            real_estate_value,
            2,
        ),
        "real_estate_loan_balance": (
            round(
                real_estate_loan_balance,
                2,
            )
        ),
        "real_estate_equity": round(
            real_estate_equity,
            2,
        ),
        "monthly_rental_cash_flow": (
            round(
                monthly_rental_cash_flow,
                2,
            )
        ),
        "net_worth": round(
            net_worth,
            2,
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