from datetime import date
from typing import Any


def parse_amount(
    value: Any,
) -> float:
    try:
        return float(
            str(value)
            .strip()
            .replace(",", "")
        )

    except (TypeError, ValueError) as error:
        raise ValueError(
            "Invalid IBKR cash movement amount."
        ) from error


def parse_settle_date(
    value: Any,
) -> date:
    try:
        return date.fromisoformat(
            str(value).strip()
        )

    except ValueError as error:
        raise ValueError(
            "Invalid IBKR cash movement date."
        ) from error


def parse_cash_movements(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cash_movements = []

    for record in records:
        currency = str(
            record.get("Currency", "")
        ).strip().upper()

        settle_date_value = str(
            record.get("Settle Date", "")
        ).strip()

        description = str(
            record.get("Description", "")
        ).strip()

        amount_value = record.get(
            "Amount",
            "",
        )

        # Praleidžiame IBKR suvestinės eilutę.
        if currency in {
            "",
            "TOTAL",
        }:
            continue

        if not settle_date_value:
            continue

        amount = parse_amount(
            amount_value
        )

        if amount == 0:
            continue

        movement_type = (
            "DEPOSIT"
            if amount > 0
            else "WITHDRAWAL"
        )

        cash_movements.append(
            {
                "broker": "Interactive Brokers",
                "movement_type": movement_type,
                "amount": abs(amount),
                "signed_amount": amount,
                "currency": currency,
                "movement_date": parse_settle_date(
                    settle_date_value
                ),
                "description": description,
                "source_row": record.get(
                    "_row_number"
                ),
            }
        )

    return cash_movements