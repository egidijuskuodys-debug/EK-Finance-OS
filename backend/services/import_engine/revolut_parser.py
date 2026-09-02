import csv
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_revolut_csv(file_path: str) -> dict[str, Any]:
    """
    Parse Revolut Trading Account Statement CSV file.

    Expected columns:
    Date,
    Ticker,
    Type,
    Quantity,
    Price per share,
    Total Amount,
    Currency,
    FX Rate
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Revolut file not found: {file_path}"
        )

    transactions: list[dict[str, Any]] = []
    dividends: list[dict[str, Any]] = []
    cash_movements: list[dict[str, Any]] = []
    unknown_rows: list[dict[str, Any]] = []

    normalized_rows: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        reader = csv.DictReader(csv_file)

        required_columns = {
            "Date",
            "Ticker",
            "Type",
            "Quantity",
            "Price per share",
            "Total Amount",
            "Currency",
            "FX Rate",
        }

        if reader.fieldnames is None:
            raise ValueError(
                "Revolut CSV does not contain "
                "a header row."
            )

        missing_columns = (
            required_columns
            - set(reader.fieldnames)
        )

        if missing_columns:
            missing = ", ".join(
                sorted(missing_columns)
            )

            raise ValueError(
                "Revolut CSV is missing "
                f"required columns: {missing}"
            )

        for row_number, row in enumerate(
            reader,
            start=2,
        ):
            if not any(
                value and value.strip()
                for value in row.values()
            ):
                continue

            normalized_rows.append(
                _normalize_row(
                    row,
                    row_number,
                )
            )

    merger_rows: list[dict[str, Any]] = []

    for parsed_row in normalized_rows:
        operation_type = parsed_row["type"]

        if operation_type.startswith("BUY"):
            transactions.append(
                _build_trade(
                    parsed_row,
                    transaction_type="BUY",
                )
            )

        elif operation_type.startswith("SELL"):
            transactions.append(
                _build_trade(
                    parsed_row,
                    transaction_type="SELL",
                )
            )

        elif operation_type == "DIVIDEND":
            dividends.append(
                _build_dividend(
                    parsed_row,
                    operation_type,
                )
            )

        elif (
            operation_type
            == "DIVIDEND TAX (CORRECTION)"
        ):
            dividends.append(
                _build_dividend(
                    parsed_row,
                    operation_type,
                )
            )

        elif operation_type in {
            "CASH TOP-UP",
            "CASH WITHDRAWAL",
            "CASH TRANSFER",
            "REWARD",
            "POSITION CLOSURE",
        }:
            cash_movements.append(
                _build_cash_movement(
                    parsed_row
                )
            )

        elif operation_type in {
            "MERGER - CASH",
            "MERGER - STOCK",
        }:
            merger_rows.append(
                parsed_row
            )

        else:
            unknown_rows.append(
                parsed_row
            )

    merger_transactions, unmatched_mergers = (
        _build_merger_transactions(
            merger_rows
        )
    )

    transactions.extend(
        merger_transactions
    )

    unknown_rows.extend(
        unmatched_mergers
    )

    transactions.sort(
        key=lambda item: item["date"]
    )

    dividends.sort(
        key=lambda item: item["date"]
    )

    cash_movements.sort(
        key=lambda item: item["date"]
    )

    unknown_rows.sort(
        key=lambda item: item["date"]
    )

    return {
        "broker": "REVOLUT",
        "file_name": path.name,
        "transactions": transactions,
        "dividends": dividends,
        "cash_movements": cash_movements,
        "unknown_rows": unknown_rows,
        "summary": {
            "transactions": len(
                transactions
            ),
            "dividends": len(
                dividends
            ),
            "cash_movements": len(
                cash_movements
            ),
            "unknown_rows": len(
                unknown_rows
            ),
        },
    }


def _build_trade(
    parsed_row: dict[str, Any],
    transaction_type: str,
) -> dict[str, Any]:
    quantity = parsed_row["quantity"]
    price = parsed_row["price_per_share"]

    if quantity is None:
        raise ValueError(
            "Revolut trade does not "
            "contain quantity. "
            f"Row: {parsed_row['row_number']}"
        )

    if price is None:
        raise ValueError(
            "Revolut trade does not "
            "contain price. "
            f"Row: {parsed_row['row_number']}"
        )

    quantity = abs(
        float(quantity)
    )

    price = abs(
        float(price)
    )

    commission = _calculate_commission(
        transaction_type=transaction_type,
        quantity=quantity,
        price=price,
        total_amount=(
            parsed_row["total_amount"]
        ),
    )

    return {
        "date": parsed_row["date"],
        "ticker": parsed_row["ticker"],
        "transaction_type": (
            transaction_type
        ),
        "quantity": quantity,
        "price": price,
        "commission": commission,
        "total_amount": (
            parsed_row["total_amount"]
        ),
        "currency": (
            parsed_row["currency"]
        ),
        "fx_rate": (
            parsed_row["fx_rate"]
        ),
        "original_type": (
            parsed_row["type"]
        ),
    }


def _build_dividend(
    parsed_row: dict[str, Any],
    operation_type: str,
) -> dict[str, Any]:
    return {
        "date": parsed_row["date"],
        "ticker": parsed_row["ticker"],
        "amount": (
            parsed_row["total_amount"]
        ),
        "currency": (
            parsed_row["currency"]
        ),
        "fx_rate": (
            parsed_row["fx_rate"]
        ),
        "original_type": (
            operation_type
        ),
    }


def _build_cash_movement(
    parsed_row: dict[str, Any],
) -> dict[str, Any]:
    return {
        "date": parsed_row["date"],
        "ticker": parsed_row["ticker"],
        "movement_type": (
            parsed_row["type"]
        ),
        "amount": (
            parsed_row["total_amount"]
        ),
        "currency": (
            parsed_row["currency"]
        ),
        "fx_rate": (
            parsed_row["fx_rate"]
        ),
    }


def _build_merger_transactions(
    merger_rows: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    transactions: list[
        dict[str, Any]
    ] = []

    unmatched: list[
        dict[str, Any]
    ] = []

    grouped: dict[
        tuple[str, object],
        list[dict[str, Any]],
    ] = {}

    for row in merger_rows:
        ticker = row["ticker"]
        merger_date = row["date"].date()

        key = (
            ticker,
            merger_date,
        )

        grouped.setdefault(
            key,
            [],
        ).append(
            row
        )

    for rows in grouped.values():
        cash_row = next(
            (
                row
                for row in rows
                if row["type"]
                == "MERGER - CASH"
            ),
            None,
        )

        stock_row = next(
            (
                row
                for row in rows
                if row["type"]
                == "MERGER - STOCK"
            ),
            None,
        )

        if (
            cash_row is None
            or stock_row is None
        ):
            unmatched.extend(
                rows
            )
            continue

        quantity = stock_row[
            "quantity"
        ]

        cash_amount = cash_row[
            "total_amount"
        ]

        if (
            quantity is None
            or cash_amount is None
        ):
            unmatched.extend(
                rows
            )
            continue

        quantity = abs(
            float(quantity)
        )

        cash_amount = abs(
            float(cash_amount)
        )

        if quantity <= 0:
            unmatched.extend(
                rows
            )
            continue

        price = (
            cash_amount
            / quantity
        )

        transactions.append(
            {
                "date": max(
                    cash_row["date"],
                    stock_row["date"],
                ),
                "ticker": (
                    stock_row["ticker"]
                ),
                "transaction_type": (
                    "SELL"
                ),
                "quantity": quantity,
                "price": price,
                "commission": 0.0,
                "total_amount": (
                    cash_amount
                ),
                "currency": (
                    cash_row["currency"]
                ),
                "fx_rate": (
                    cash_row["fx_rate"]
                ),
                "original_type": (
                    "MERGER"
                ),
            }
        )

    return (
        transactions,
        unmatched,
    )


def _calculate_commission(
    transaction_type: str,
    quantity: float,
    price: float,
    total_amount: float | None,
) -> float:
    if total_amount is None:
        return 0.0

    gross_value = (
        quantity
        * price
    )

    statement_total = abs(
        float(total_amount)
    )

    if transaction_type == "BUY":
        commission = (
            statement_total
            - gross_value
        )

    elif transaction_type == "SELL":
        commission = (
            gross_value
            - statement_total
        )

    else:
        return 0.0

    commission = round(
        commission,
        2,
    )

    if commission < 0:
        return 0.0

    return commission


def _normalize_row(
    row: dict[str, str | None],
    row_number: int,
) -> dict[str, Any]:
    try:
        return {
            "row_number": row_number,
            "date": _parse_datetime(
                row.get("Date")
            ),
            "ticker": _clean_text(
                row.get("Ticker")
            ),
            "type": _clean_text(
                row.get("Type")
            ).upper(),
            "quantity": (
                _parse_optional_float(
                    row.get("Quantity")
                )
            ),
            "price_per_share": (
                _parse_money(
                    row.get(
                        "Price per share"
                    )
                )
            ),
            "total_amount": (
                _parse_money(
                    row.get(
                        "Total Amount"
                    )
                )
            ),
            "currency": _clean_text(
                row.get("Currency")
            ).upper(),
            "fx_rate": (
                _parse_optional_float(
                    row.get("FX Rate")
                )
            ),
        }

    except Exception as exc:
        raise ValueError(
            "Failed to parse Revolut "
            f"CSV row {row_number}: {row}"
        ) from exc


def _parse_datetime(
    value: str | None,
) -> datetime:
    cleaned = _clean_text(
        value
    )

    if not cleaned:
        raise ValueError(
            "Missing transaction date."
        )

    normalized = cleaned.replace(
        "Z",
        "+00:00",
    )

    return datetime.fromisoformat(
        normalized
    )


def _parse_money(
    value: str | None,
) -> float | None:
    """
    Parse Revolut monetary values.

    Examples:
        EUR 50
        USD 25.40
        123.45
        EUR -12.30
    """

    cleaned = _clean_text(
        value
    )

    if not cleaned:
        return None

    cleaned = cleaned.replace(
        "\u00a0",
        " ",
    )

    cleaned = re.sub(
        r"^[A-Za-z]{3}\s*",
        "",
        cleaned,
    )

    cleaned = cleaned.replace(
        ",",
        "",
    )

    return float(
        cleaned
    )


def _parse_optional_float(
    value: str | None,
) -> float | None:
    cleaned = _clean_text(
        value
    )

    if not cleaned:
        return None

    cleaned = cleaned.replace(
        "\u00a0",
        " ",
    )

    cleaned = cleaned.replace(
        ",",
        "",
    )

    return float(
        cleaned
    )


def _clean_text(
    value: str | None,
) -> str:
    if value is None:
        return ""

    return value.strip()