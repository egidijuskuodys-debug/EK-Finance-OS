import re
from datetime import date
from typing import Any


TICKER_PATTERN = re.compile(
    r"^\s*([A-Z0-9.\-]+)\s*\("
)


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
            "Invalid IBKR dividend amount."
        ) from error


def parse_dividend_date(
    value: Any,
) -> date:
    try:
        return date.fromisoformat(
            str(value).strip()
        )

    except ValueError as error:
        raise ValueError(
            "Invalid IBKR dividend date."
        ) from error


def extract_ticker(
    description: str,
) -> str:
    match = TICKER_PATTERN.search(
        description
    )

    if match is None:
        raise ValueError(
            "Ticker could not be extracted "
            "from dividend description."
        )

    return match.group(1).upper()


def parse_dividends(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    dividends = []

    for record in records:
        currency = str(
            record.get("Currency", "")
        ).strip().upper()

        payment_date_value = str(
            record.get("Date", "")
        ).strip()

        description = str(
            record.get("Description", "")
        ).strip()

        amount_value = record.get(
            "Amount",
            "",
        )

        # Praleidžiame IBKR suvestines,
        # pvz. Currency = Total
        if currency in {
            "",
            "TOTAL",
        }:
            continue

        if not payment_date_value:
            continue

        if not description:
            continue

        gross_amount = parse_amount(
            amount_value
        )

        if gross_amount <= 0:
            continue

        ticker = extract_ticker(
            description
        )

        dividends.append(
            {
                "broker": "Interactive Brokers",
                "ticker": ticker,
                "payment_date": parse_dividend_date(
                    payment_date_value
                ),
                "gross_amount": round(
                    gross_amount,
                    2,
                ),
                "tax_amount": 0.0,
                "net_amount": round(
                    gross_amount,
                    2,
                ),
                "currency": currency,
                "description": description,
                "source_row": record.get(
                    "_row_number"
                ),
            }
        )

    return dividends