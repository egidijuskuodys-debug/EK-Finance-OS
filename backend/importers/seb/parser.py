import re
from datetime import datetime
from hashlib import sha256
from typing import Any


INSTRUMENT_PATTERN = re.compile(
    r"^Vertybinių popierių pavadinimas\s+"
    r"(?P<description>.+?)\s+"
    r"(?P<isin>[A-Z]{2}[A-Z0-9]{9}\d)$"
)

NUMBER_PATTERN = (
    r"(?:\d{1,3}(?: \d{3})+|\d+)"
    r"(?:,\d+)?"
)

SIGNED_NUMBER_PATTERN = (
    r"[+-]"
    r"(?:\d{1,3}(?: \d{3})+|\d+)"
    r"(?:,\d+)?"
)

TRANSACTION_PATTERN = re.compile(
    rf"^(?P<date>\d{{4}}-\d{{2}}-\d{{2}})\s+"
    rf"(?P<operation_code>[A-Z]+)\s+"
    rf"(?P<price>{NUMBER_PATTERN})\s+"
    rf"(?P<price_unit>%|[A-Z]{{3}})\s+"
    rf"(?:(?P<price_currency>[A-Z]{{3}})\s+)?"
    rf"(?P<quantity>{SIGNED_NUMBER_PATTERN})\s+"
    rf"(?P<amount>{NUMBER_PATTERN})\s+"
    rf"(?P<amount_currency>[A-Z]{{3}})$"
)


def _parse_decimal(
    value: str,
) -> float:
    normalized = (
        value
        .replace(" ", "")
        .replace(",", ".")
    )

    return float(normalized)


def _parse_date(
    value: str,
):
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        ).date()

    except ValueError as error:
        raise ValueError(
            "Invalid SEB transaction date."
        ) from error


def _clean_description(
    description: str,
    isin: str,
) -> str:
    cleaned = (
        description
        .replace("„", "")
        .replace("“", "")
        .replace('"', "")
        .strip()
    )

    cleaned = re.sub(
        rf"^{re.escape(isin)}\s+",
        "",
        cleaned,
    )

    seb_prefix_pattern = re.compile(
        r"^[A-Z0-9]+ "
        r"(?:LX|SS|GY)\s+"
    )

    cleaned = (
        seb_prefix_pattern.sub(
            "",
            cleaned,
        )
    )

    cleaned = " ".join(
        cleaned.split()
    )

    return cleaned


def _get_transaction_type(
    operation_code: str,
    quantity: float,
    amount: float,
) -> str:
    if operation_code in {
        "SUBS",
        "TRAD",
    }:
        if quantity > 0:
            return "BUY"

        if quantity < 0:
            return "SELL"

        raise ValueError(
            "SEB trade transaction "
            "has zero quantity."
        )

    if operation_code == "CORP":
        if (
            quantity > 0
            and amount == 0
        ):
            return "QUANTITY_ADJUSTMENT"

        if (
            quantity < 0
            and amount > 0
        ):
            return "REDEMPTION"

        raise ValueError(
            "Unsupported SEB CORP "
            "transaction combination: "
            f"quantity={quantity}, "
            f"amount={amount}."
        )

    raise ValueError(
        "Unsupported SEB transaction "
        f"type: {operation_code!r}."
    )


def _get_asset_type(
    description: str,
    price_unit: str,
) -> str:
    normalized = description.upper()

    if price_unit == "%":
        return "Bond"

    if (
        "ISHARES" in normalized
        or "UCITS ETF" in normalized
        or " ETF " in f" {normalized} "
    ):
        return "ETF"

    if (
        "FUND" in normalized
        or "SEB ACTIVE" in normalized
    ):
        return "Fund"

    return "Security"


def _build_broker_transaction_id(
    isin: str,
    transaction_type: str,
    operation_code: str,
    transaction_date,
    quantity: float,
    price: float,
    amount: float,
    currency: str,
) -> str:
    raw_value = "|".join(
        [
            "SEB",
            isin,
            transaction_type,
            operation_code,
            transaction_date.isoformat(),
            f"{quantity:.10f}",
            f"{price:.10f}",
            f"{amount:.10f}",
            currency,
        ]
    )

    return sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def parse_seb_ocr_pages(
    pages: list[str],
) -> dict[str, list[dict[str, Any]]]:
    transactions: list[
        dict[str, Any]
    ] = []

    current_instrument: (
        dict[str, str] | None
    ) = None

    for page_number, page in enumerate(
        pages,
        start=1,
    ):
        for raw_line in page.splitlines():
            line = raw_line.strip()

            if not line:
                continue

            instrument_match = (
                INSTRUMENT_PATTERN.match(
                    line
                )
            )

            if instrument_match:
                isin = (
                    instrument_match.group(
                        "isin"
                    )
                    .strip()
                    .upper()
                )

                raw_description = (
                    instrument_match.group(
                        "description"
                    ).strip()
                )

                current_instrument = {
                    "description": (
                        _clean_description(
                            raw_description,
                            isin,
                        )
                    ),
                    "isin": isin,
                }

                continue

            transaction_match = (
                TRANSACTION_PATTERN.match(
                    line
                )
            )

            if not transaction_match:
                continue

            if current_instrument is None:
                raise ValueError(
                    "SEB transaction found "
                    "before instrument header."
                )

            operation_code = (
                transaction_match.group(
                    "operation_code"
                )
            )

            price_unit = (
                transaction_match.group(
                    "price_unit"
                )
            )

            price_currency = (
                transaction_match.group(
                    "price_currency"
                )
            )

            amount_currency = (
                transaction_match.group(
                    "amount_currency"
                )
            )

            if price_unit == "%":
                currency = amount_currency
            else:
                currency = price_unit

            if (
                price_currency is not None
                and price_currency
                != amount_currency
            ):
                raise ValueError(
                    "SEB transaction currency "
                    "mismatch."
                )

            if currency != amount_currency:
                raise ValueError(
                    "SEB transaction currency "
                    "mismatch."
                )

            signed_quantity = _parse_decimal(
                transaction_match.group(
                    "quantity"
                )
            )

            amount = _parse_decimal(
                transaction_match.group(
                    "amount"
                )
            )

            quoted_price = _parse_decimal(
                transaction_match.group(
                    "price"
                )
            )

            transaction_date = _parse_date(
                transaction_match.group(
                    "date"
                )
            )

            transaction_type = (
                _get_transaction_type(
                    operation_code,
                    signed_quantity,
                    amount,
                )
            )

            quantity = abs(
                signed_quantity
            )

            if price_unit == "%":
                effective_price = (
                    amount / quantity
                    if quantity > 0
                    else 0.0
                )
            else:
                effective_price = (
                    quoted_price
                )

            description = (
                current_instrument[
                    "description"
                ]
            )

            isin = (
                current_instrument[
                    "isin"
                ]
            )

            asset_type = (
                _get_asset_type(
                    description,
                    price_unit,
                )
            )

            broker_transaction_id = (
                _build_broker_transaction_id(
                    isin=isin,
                    transaction_type=(
                        transaction_type
                    ),
                    operation_code=(
                        operation_code
                    ),
                    transaction_date=(
                        transaction_date
                    ),
                    quantity=quantity,
                    price=effective_price,
                    amount=amount,
                    currency=currency,
                )
            )

            transactions.append(
                {
                    "broker": "SEB",
                    "ticker": isin,
                    "market_ticker": None,
                    "asset": description,
                    "asset_type": asset_type,
                    "broker_transaction_id": (
                        broker_transaction_id
                    ),
                    "transaction_type": (
                        transaction_type
                    ),
                    "quantity": quantity,
                    "price": effective_price,
                    "commission": 0.0,
                    "currency": currency,
                    "transaction_date": (
                        transaction_date
                    ),
                    "settlement_date": (
                        transaction_date
                    ),
                    "operation_code": (
                        operation_code
                    ),
                    "isin": isin,
                    "description": (
                        description
                    ),
                    "amount": amount,
                    "quoted_price": (
                        quoted_price
                    ),
                    "price_unit": (
                        price_unit
                    ),
                    "signed_quantity": (
                        signed_quantity
                    ),
                    "source_page": (
                        page_number
                    ),
                }
            )

    return {
        "transactions": transactions,
        "dividends": [],
        "cash_movements": [],
        "positions": [],
        "fees": [],
    }