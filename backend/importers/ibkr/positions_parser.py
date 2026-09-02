from typing import Any

from services.asset_classification_service import (
    classify_asset_type,
)


def parse_number(
    value: Any,
    field_name: str,
) -> float:
    try:
        return float(
            str(value)
            .strip()
            .replace(",", "")
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Invalid number in field "
            f"'{field_name}'."
        ) from error


def parse_positions(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    positions = []

    for record in records:
        data_discriminator = str(
            record.get(
                "DataDiscriminator",
                "",
            )
        ).strip()

        asset_category = str(
            record.get(
                "Asset Category",
                "",
            )
        ).strip()

        if data_discriminator != "Summary":
            continue

        if asset_category != "Stocks":
            continue

        ticker = str(
            record.get(
                "Symbol",
                "",
            )
        ).strip().upper()

        currency = str(
            record.get(
                "Currency",
                "",
            )
        ).strip().upper()

        if not ticker:
            continue

        quantity = parse_number(
            record.get(
                "Quantity"
            ),
            "Quantity",
        )

        if quantity <= 0:
            continue

        purchase_price = parse_number(
            record.get(
                "Cost Price"
            ),
            "Cost Price",
        )

        current_price = parse_number(
            record.get(
                "Close Price"
            ),
            "Close Price",
        )

        asset_type = (
            classify_asset_type(
                ticker=ticker,
                broker_asset_category=(
                    asset_category
                ),
            )
        )

        positions.append(
            {
                "broker": (
                    "Interactive Brokers"
                ),
                "asset": ticker,
                "ticker": ticker,
                "market_ticker": ticker,
                "asset_type": (
                    asset_type
                ),
                "quantity": quantity,
                "purchase_price": (
                    purchase_price
                ),
                "current_price": (
                    current_price
                ),
                "currency": currency,
                "source_row": record.get(
                    "_row_number"
                ),
            }
        )

    return positions