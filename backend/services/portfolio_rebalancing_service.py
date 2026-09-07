from sqlalchemy.orm import Session

from services.analytics_service import get_allocation
from services.portfolio_target_service import (
    get_portfolio_targets,
)


DIMENSION_ALLOCATION_KEYS = {
    "asset_type": ("by_asset_type", "asset_type"),
    "broker": ("by_broker", "broker"),
}


def _normalize(value: str) -> str:
    return value.strip().casefold()


def get_portfolio_rebalancing(db: Session):
    allocation = get_allocation(db)
    targets = get_portfolio_targets(db)

    portfolio_value = float(
        allocation.get("portfolio_value", 0)
    )
    base_currency = allocation.get(
        "base_currency",
        "EUR",
    )

    current_lookup = {}

    for dimension, (
        allocation_key,
        item_key,
    ) in DIMENSION_ALLOCATION_KEYS.items():
        current_lookup[dimension] = {
            _normalize(str(item[item_key])): item
            for item in allocation.get(allocation_key, [])
        }

    items = []

    for target in targets:
        dimension = target.dimension
        target_key = target.target_key
        target_percentage = float(
            target.target_percentage
        )

        dimension_values = current_lookup.get(
            dimension,
            {},
        )
        current = dimension_values.get(
            _normalize(target_key),
        )

        current_value = (
            float(current.get("value", 0))
            if current
            else 0.0
        )
        current_percentage = (
            float(current.get("percentage", 0))
            if current
            else 0.0
        )

        target_value = (
            portfolio_value
            * target_percentage
            / 100
        )
        difference = target_value - current_value
        deviation = (
            current_percentage
            - target_percentage
        )

        if abs(difference) < 0.01:
            action = "Hold"
        elif difference > 0:
            action = "Add"
        else:
            action = "Reduce"

        items.append(
            {
                "dimension": dimension,
                "target_key": target_key,
                "current_value": round(
                    current_value,
                    2,
                ),
                "current_percentage": round(
                    current_percentage,
                    2,
                ),
                "target_value": round(
                    target_value,
                    2,
                ),
                "target_percentage": round(
                    target_percentage,
                    2,
                ),
                "difference": round(
                    difference,
                    2,
                ),
                "deviation_percentage_points": round(
                    deviation,
                    2,
                ),
                "action": action,
                "currency": base_currency,
            }
        )

    items.sort(
        key=lambda item: (
            item["dimension"],
            -abs(item["difference"]),
        )
    )

    return {
        "portfolio_value": round(
            portfolio_value,
            2,
        ),
        "base_currency": base_currency,
        "targets_count": len(items),
        "items": items,
    }
