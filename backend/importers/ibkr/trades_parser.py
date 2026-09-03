from datetime import datetime
from hashlib import sha256
from typing import Any


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
            f"Invalid number in field '{field_name}'."
        ) from error


def parse_ibkr_datetime(
    value: Any,
) -> datetime:
    try:
        return datetime.strptime(
            str(value).strip(),
            "%Y-%m-%d, %H:%M:%S",
        )

    except ValueError as error:
        raise ValueError(
            "Invalid IBKR trade date format."
        ) from error


def build_broker_transaction_id(
    symbol: str,
    transaction_type: str,
    quantity: float,
    price: float,
    currency: str,
    trade_datetime: datetime,
    commission: float,
) -> str:
    raw_value = "|".join(
        [
            "IBKR",
            symbol,
            transaction_type,
            f"{quantity:.10f}",
            f"{price:.10f}",
            currency,
            trade_datetime.isoformat(),
            f"{commission:.10f}",
        ]
    )

    return sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def parse_trades(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    transactions = []

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

        if data_discriminator != "Order":
            continue

        if asset_category != "Stocks":
            continue

        symbol = str(
            record.get("Symbol", "")
        ).strip().upper()

        currency = str(
            record.get("Currency", "")
        ).strip().upper()

        if not symbol:
            continue

        quantity_signed = parse_number(
            record.get("Quantity"),
            "Quantity",
        )

        if quantity_signed == 0:
            continue

        transaction_type = (
            "BUY"
            if quantity_signed > 0
            else "SELL"
        )

        quantity = abs(quantity_signed)

        price = parse_number(
            record.get("T. Price"),
            "T. Price",
        )

        commission = abs(
            parse_number(
                record.get(
                    "Comm/Fee",
                    0,
                )
                or 0,
                "Comm/Fee",
            )
        )

        trade_datetime = parse_ibkr_datetime(
            record.get("Date/Time")
        )

        broker_transaction_id = (
            build_broker_transaction_id(
                symbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                price=price,
                currency=currency,
                trade_datetime=trade_datetime,
                commission=commission,
            )
        )

        transactions.append(
            {
                "broker": "Interactive Brokers",
                "ticker": symbol,
                "market_ticker": symbol,
                "asset_type": "Stock",
                "broker_transaction_id": (
                    broker_transaction_id
                ),
                "transaction_type": (
                    transaction_type
                ),
                "quantity": quantity,
                "price": price,
                "commission": commission,
                "currency": currency,
                "transaction_date": (
                    trade_datetime.date()
                ),
                "transaction_datetime": (
                    trade_datetime
                ),
                "source_row": record.get(
                    "_row_number"
                ),
            }
        )

    return transactions


def parse_forex_cash_movements(
    records: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    cash_movements = []

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

        if data_discriminator != "Order":
            continue

        if asset_category != "Forex":
            continue

        symbol = str(
            record.get(
                "Symbol",
                "",
            )
        ).strip().upper()

        if "." not in symbol:
            continue

        base_currency, quote_currency = (
            symbol.split(".", 1)
        )

        quantity_signed = parse_number(
            record.get("Quantity"),
            "Quantity",
        )

        proceeds_signed = parse_number(
            record.get("Proceeds"),
            "Proceeds",
        )

        if (
            quantity_signed == 0
            and proceeds_signed == 0
        ):
            continue

        trade_datetime = parse_ibkr_datetime(
            record.get("Date/Time")
        )

        description = (
            f"IBKR Forex {symbol}"
        )

        if quantity_signed != 0:
            cash_movements.append(
                {
                    "broker": (
                        "Interactive Brokers"
                    ),
                    "movement_type": (
                        "FOREX"
                    ),
                    "amount": (
                        quantity_signed
                    ),
                    "currency": (
                        base_currency
                    ),
                    "movement_date": (
                        trade_datetime.date()
                    ),
                    "transaction_datetime": (
                        trade_datetime
                    ),
                    "description": (
                        description
                    ),
                    "source_row": record.get(
                        "_row_number"
                    ),
                }
            )

        if proceeds_signed != 0:
            cash_movements.append(
                {
                    "broker": (
                        "Interactive Brokers"
                    ),
                    "movement_type": (
                        "FOREX"
                    ),
                    "amount": (
                        proceeds_signed
                    ),
                    "currency": (
                        quote_currency
                    ),
                    "movement_date": (
                        trade_datetime.date()
                    ),
                    "transaction_datetime": (
                        trade_datetime
                    ),
                    "description": (
                        description
                    ),
                    "source_row": record.get(
                        "_row_number"
                    ),
                }
            )

    return cash_movements