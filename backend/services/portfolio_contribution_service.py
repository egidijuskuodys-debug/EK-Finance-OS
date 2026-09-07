from sqlalchemy.orm import Session

from services.analytics_service import get_allocation
from services.portfolio_target_service import (
    get_portfolio_targets,
)


DIMENSION_CONFIG = {
    "asset_type": {
        "allocation_key": "by_asset_type",
        "item_key": "asset_type",
    },
    "broker": {
        "allocation_key": "by_broker",
        "item_key": "broker",
    },
}


def _normalize(value: str) -> str:
    return value.strip().casefold()


def _build_dimension_plan(
    allocation: dict,
    targets: list,
    dimension: str,
    contribution_amount: float,
):
    config = DIMENSION_CONFIG[dimension]

    current_items = {
        _normalize(str(item[config["item_key"]])): item
        for item in allocation.get(
            config["allocation_key"],
            [],
        )
    }

    portfolio_value = float(
        allocation.get("portfolio_value", 0)
    )
    future_portfolio_value = (
        portfolio_value + contribution_amount
    )

    candidates = []

    for target in targets:
        if target.dimension != dimension:
            continue

        current = current_items.get(
            _normalize(target.target_key),
        )
        current_value = (
            float(current.get("value", 0))
            if current
            else 0.0
        )
        target_percentage = float(
            target.target_percentage
        )
        future_target_value = (
            future_portfolio_value
            * target_percentage
            / 100
        )
        funding_gap = max(
            future_target_value - current_value,
            0.0,
        )

        candidates.append(
            {
                "target_key": target.target_key,
                "current_value": current_value,
                "target_percentage": target_percentage,
                "future_target_value": future_target_value,
                "funding_gap": funding_gap,
            }
        )

    total_gap = sum(
        item["funding_gap"]
        for item in candidates
    )
    positive_indexes = [
        index
        for index, item in enumerate(candidates)
        if item["funding_gap"] > 0
    ]
    last_positive_index = (
        positive_indexes[-1]
        if positive_indexes
        else None
    )

    allocations = []
    allocated_total = 0.0

    for index, item in enumerate(candidates):
        if total_gap <= 0 or item["funding_gap"] <= 0:
            suggested_amount = 0.0
        elif index == last_positive_index:
            suggested_amount = (
                contribution_amount - allocated_total
            )
        else:
            suggested_amount = round(
                contribution_amount
                * item["funding_gap"]
                / total_gap,
                2,
            )
            allocated_total += suggested_amount

        future_value = (
            item["current_value"]
            + suggested_amount
        )
        future_percentage = (
            future_value
            / future_portfolio_value
            * 100
            if future_portfolio_value > 0
            else 0.0
        )

        allocations.append(
            {
                "target_key": item["target_key"],
                "current_value": round(
                    item["current_value"],
                    2,
                ),
                "target_percentage": round(
                    item["target_percentage"],
                    2,
                ),
                "suggested_amount": round(
                    suggested_amount,
                    2,
                ),
                "future_value": round(
                    future_value,
                    2,
                ),
                "future_percentage": round(
                    future_percentage,
                    2,
                ),
            }
        )

    allocations.sort(
        key=lambda item: -item["suggested_amount"]
    )

    return {
        "dimension": dimension,
        "contribution_amount": round(
            contribution_amount,
            2,
        ),
        "allocated_amount": round(
            sum(
                item["suggested_amount"]
                for item in allocations
            ),
            2,
        ),
        "allocations": allocations,
    }


def get_contribution_plan(
    db: Session,
    contribution_amount: float,
):
    if contribution_amount <= 0:
        raise ValueError(
            "Contribution amount must be greater than zero."
        )

    allocation = get_allocation(db)
    targets = get_portfolio_targets(db)

    groups = [
        _build_dimension_plan(
            allocation,
            targets,
            dimension,
            contribution_amount,
        )
        for dimension in DIMENSION_CONFIG
    ]

    return {
        "portfolio_value": round(
            float(allocation.get("portfolio_value", 0)),
            2,
        ),
        "contribution_amount": round(
            contribution_amount,
            2,
        ),
        "future_portfolio_value": round(
            float(allocation.get("portfolio_value", 0))
            + contribution_amount,
            2,
        ),
        "base_currency": allocation.get(
            "base_currency",
            "EUR",
        ),
        "groups": groups,
    }
