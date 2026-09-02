from datetime import date
from typing import Any


SUPPORTED_TRANSACTION_TYPES = {
    "BUY",
    "SELL",
}


def validate_required_fields(
    record: dict[str, Any],
    required_fields: set[str],
) -> None:
    missing_fields = [
        field
        for field in required_fields
        if record.get(field) in (None, "")
    ]

    if missing_fields:
        missing = ", ".join(
            sorted(missing_fields)
        )

        raise ValueError(
            f"Missing required fields: {missing}."
        )


def validate_positive_number(
    value: Any,
    field_name: str,
) -> float:
    try:
        numeric_value = float(value)

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Field '{field_name}' must be a number."
        ) from error

    if numeric_value <= 0:
        raise ValueError(
            f"Field '{field_name}' must be greater than 0."
        )

    return numeric_value


def validate_non_negative_number(
    value: Any,
    field_name: str,
) -> float:
    try:
        numeric_value = float(value)

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Field '{field_name}' must be a number."
        ) from error

    if numeric_value < 0:
        raise ValueError(
            f"Field '{field_name}' cannot be negative."
        )

    return numeric_value


def validate_transaction_type(
    transaction_type: Any,
) -> str:
    normalized_type = str(
        transaction_type
    ).strip().upper()

    if normalized_type not in SUPPORTED_TRANSACTION_TYPES:
        raise ValueError(
            "Transaction type must be BUY or SELL."
        )

    return normalized_type


def validate_currency(
    currency: Any,
) -> str:
    normalized_currency = str(
        currency
    ).strip().upper()

    if len(normalized_currency) < 3:
        raise ValueError(
            "Currency code must contain "
            "at least 3 characters."
        )

    if len(normalized_currency) > 10:
        raise ValueError(
            "Currency code cannot exceed "
            "10 characters."
        )

    return normalized_currency


def validate_date(
    value: Any,
    field_name: str,
) -> date:
    if isinstance(value, date):
        return value

    try:
        return date.fromisoformat(
            str(value).strip()
        )

    except ValueError as error:
        raise ValueError(
            f"Field '{field_name}' must use "
            "YYYY-MM-DD format."
        ) from error


def build_transaction_duplicate_key(
    record: dict[str, Any],
) -> tuple[Any, ...]:
    return (
        record.get("broker"),
        record.get("ticker"),
        record.get("transaction_type"),
        record.get("quantity"),
        record.get("price"),
        record.get("currency"),
        record.get("transaction_date"),
    )


def build_dividend_duplicate_key(
    record: dict[str, Any],
) -> tuple[Any, ...]:
    return (
        record.get("broker"),
        record.get("ticker"),
        record.get("payment_date"),
        record.get("gross_amount"),
        record.get("tax_amount"),
        record.get("currency"),
    )


def find_duplicate_records(
    records: list[dict[str, Any]],
    key_builder,
) -> list[int]:
    seen_keys = set()
    duplicate_indexes = []

    for index, record in enumerate(
        records,
        start=1,
    ):
        record_key = key_builder(record)

        if record_key in seen_keys:
            duplicate_indexes.append(index)

        else:
            seen_keys.add(record_key)

    return duplicate_indexes