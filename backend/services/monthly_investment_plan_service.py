from datetime import date

from sqlalchemy.orm import Session

from services.portfolio_actions_service import (
    get_portfolio_actions,
)
from services.portfolio_contribution_service import (
    get_contribution_plan,
)
from services.portfolio_rebalancing_service import (
    get_portfolio_rebalancing,
)


def _get_group(
    contribution_plan: dict,
    dimension: str,
) -> dict:
    return next(
        (
            group
            for group
            in contribution_plan.get(
                "groups",
                [],
            )
            if group.get("dimension")
            == dimension
        ),
        {
            "dimension": dimension,
            "allocations": [],
        },
    )


def _calculate_current_percentage(
    current_value: float,
    portfolio_value: float,
) -> float:
    if portfolio_value <= 0:
        return 0.0

    return (
        current_value
        / portfolio_value
        * 100
    )


def _build_invest_now_items(
    group: dict,
    portfolio_value: float,
    currency: str,
) -> list:
    items = []

    for allocation in group.get(
        "allocations",
        [],
    ):
        suggested_amount = float(
            allocation.get(
                "suggested_amount",
                0.0,
            )
        )

        if suggested_amount <= 0:
            continue

        current_value = float(
            allocation.get(
                "current_value",
                0.0,
            )
        )

        current_percentage = (
            _calculate_current_percentage(
                current_value,
                portfolio_value,
            )
        )

        target_percentage = float(
            allocation.get(
                "target_percentage",
                0.0,
            )
        )

        target_key = str(
            allocation.get(
                "target_key",
                "",
            )
        )

        items.append(
            {
                "target": target_key,
                "amount": round(
                    suggested_amount,
                    2,
                ),
                "currency": currency,
                "current_percentage": round(
                    current_percentage,
                    2,
                ),
                "future_percentage": round(
                    float(
                        allocation.get(
                            "future_percentage",
                            0.0,
                        )
                    ),
                    2,
                ),
                "target_percentage": round(
                    target_percentage,
                    2,
                ),
                "priority": (
                    "High"
                    if (
                        target_percentage
                        - current_percentage
                    ) >= 10
                    else "Medium"
                ),
                "reason": (
                    f"{target_key} is below "
                    f"its {target_percentage:.2f}% "
                    "portfolio target."
                ),
            }
        )

    items.sort(
        key=lambda item: (
            -item["amount"],
            item["target"],
        )
    )

    return items


def _build_broker_routing_items(
    group: dict,
    portfolio_value: float,
    currency: str,
) -> list:
    items = []

    for allocation in group.get(
        "allocations",
        [],
    ):
        suggested_amount = float(
            allocation.get(
                "suggested_amount",
                0.0,
            )
        )

        if suggested_amount <= 0:
            continue

        current_value = float(
            allocation.get(
                "current_value",
                0.0,
            )
        )

        target_key = str(
            allocation.get(
                "target_key",
                "",
            )
        )

        target_percentage = float(
            allocation.get(
                "target_percentage",
                0.0,
            )
        )

        items.append(
            {
                "broker": target_key,
                "amount": round(
                    suggested_amount,
                    2,
                ),
                "currency": currency,
                "current_percentage": round(
                    _calculate_current_percentage(
                        current_value,
                        portfolio_value,
                    ),
                    2,
                ),
                "future_percentage": round(
                    float(
                        allocation.get(
                            "future_percentage",
                            0.0,
                        )
                    ),
                    2,
                ),
                "target_percentage": round(
                    target_percentage,
                    2,
                ),
                "reason": (
                    "Broker allocation is below "
                    "its configured target."
                ),
            }
        )

    items.sort(
        key=lambda item: (
            -item["amount"],
            item["broker"],
        )
    )

    return items


def _build_pause_items(
    rebalancing: dict,
) -> list:
    items = []

    for item in rebalancing.get(
        "items",
        [],
    ):
        if item.get("action") != "Reduce":
            continue

        dimension = str(
            item.get(
                "dimension",
                "",
            )
        )

        target = str(
            item.get(
                "target_key",
                "",
            )
        )

        current_percentage = float(
            item.get(
                "current_percentage",
                0.0,
            )
        )

        target_percentage = float(
            item.get(
                "target_percentage",
                0.0,
            )
        )

        items.append(
            {
                "dimension": dimension,
                "target": target,
                "action": (
                    "Pause new contributions"
                ),
                "current_percentage": round(
                    current_percentage,
                    2,
                ),
                "target_percentage": round(
                    target_percentage,
                    2,
                ),
                "amount_over_target": round(
                    abs(
                        float(
                            item.get(
                                "difference",
                                0.0,
                            )
                        )
                    ),
                    2,
                ),
                "currency": item.get(
                    "currency",
                    rebalancing.get(
                        "base_currency",
                        "EUR",
                    ),
                ),
                "reason": (
                    f"{target} is "
                    f"{abs(current_percentage - target_percentage):.2f} "
                    "percentage points above "
                    "its configured target."
                ),
            }
        )

    items.sort(
        key=lambda item: (
            -item["amount_over_target"],
            item["dimension"],
            item["target"],
        )
    )

    return items


def _build_review_items(
    portfolio_actions: dict,
) -> list:
    priority_order = {
        "High": 0,
        "Medium": 1,
        "Low": 2,
    }

    items = []

    for action in portfolio_actions.get(
        "actions",
        [],
    ):
        action_type = str(
            action.get(
                "action_type",
                "",
            )
        )

        if action_type not in {
            "Review",
            "Monitor",
            "Consider",
        }:
            continue

        items.append(
            {
                "category": action.get(
                    "category",
                    "",
                ),
                "priority": action.get(
                    "priority",
                    "Low",
                ),
                "action": action_type,
                "title": action.get(
                    "title",
                    "",
                ),
                "message": action.get(
                    "message",
                    "",
                ),
                "reason": action.get(
                    "reason",
                    "",
                ),
            }
        )

    items.sort(
        key=lambda item: (
            priority_order.get(
                item["priority"],
                99,
            ),
            item["category"],
            item["title"],
        )
    )

    return items


def get_monthly_investment_plan(
    db: Session,
    monthly_amount: float,
):
    if monthly_amount <= 0:
        raise ValueError(
            "Monthly amount must be "
            "greater than zero."
        )

    contribution_plan = (
        get_contribution_plan(
            db=db,
            contribution_amount=(
                monthly_amount
            ),
        )
    )

    rebalancing = (
        get_portfolio_rebalancing(
            db
        )
    )

    portfolio_actions = (
        get_portfolio_actions(
            db
        )
    )

    portfolio_value = float(
        contribution_plan.get(
            "portfolio_value",
            0.0,
        )
    )

    currency = str(
        contribution_plan.get(
            "base_currency",
            "EUR",
        )
    )

    asset_group = _get_group(
        contribution_plan,
        "asset_type",
    )

    broker_group = _get_group(
        contribution_plan,
        "broker",
    )

    invest_now = (
        _build_invest_now_items(
            group=asset_group,
            portfolio_value=(
                portfolio_value
            ),
            currency=currency,
        )
    )

    broker_routing = (
        _build_broker_routing_items(
            group=broker_group,
            portfolio_value=(
                portfolio_value
            ),
            currency=currency,
        )
    )

    pause_new_contributions = (
        _build_pause_items(
            rebalancing
        )
    )

    review_items = (
        _build_review_items(
            portfolio_actions
        )
    )

    allocated_amount = round(
        sum(
            item["amount"]
            for item in invest_now
        ),
        2,
    )

    unallocated_amount = round(
        max(
            monthly_amount
            - allocated_amount,
            0.0,
        ),
        2,
    )

    return {
        "generated_date": (
            date.today().isoformat()
        ),
        "currency": currency,
        "portfolio_value": round(
            portfolio_value,
            2,
        ),
        "monthly_amount": round(
            monthly_amount,
            2,
        ),
        "allocated_amount": (
            allocated_amount
        ),
        "unallocated_amount": (
            unallocated_amount
        ),
        "summary": {
            "invest_now_count": len(
                invest_now
            ),
            "broker_routes_count": len(
                broker_routing
            ),
            "pause_count": len(
                pause_new_contributions
            ),
            "review_count": len(
                review_items
            ),
        },
        "invest_now": invest_now,
        "broker_routing": (
            broker_routing
        ),
        "pause_new_contributions": (
            pause_new_contributions
        ),
        "review_items": review_items,
        "guidance": {
            "asset_and_broker_note": (
                "Asset type and broker are "
                "two views of the same monthly "
                "amount. Do not add their totals."
            ),
            "sell_note": (
                "Reduce and review signals are "
                "not automatic sell instructions. "
                "Check taxes, fees and the original "
                "investment thesis before selling."
            ),
        },
    }