import hashlib
from typing import Any

from importers.base_importer import BaseImporter
from services.import_engine.revolut_parser import (
    parse_revolut_csv,
)


class RevolutImporter(BaseImporter):
    def get_broker_name(self) -> str:
        return "REVOLUT"

    def validate_structure(self) -> None:
        parsed = parse_revolut_csv(
            str(self.file_path)
        )

        if parsed.get("broker") != "REVOLUT":
            raise ValueError(
                "File is not recognized as a "
                "Revolut trading statement."
            )

    def parse(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        parsed = parse_revolut_csv(
            str(self.file_path)
        )

        transactions = self._build_transactions(
            parsed.get(
                "transactions",
                [],
            )
        )

        dividends = self._build_dividends(
            parsed.get(
                "dividends",
                [],
            )
        )

        cash_movements = self._build_cash_movements(
            parsed.get(
                "cash_movements",
                [],
            )
        )

        return {
            "transactions": transactions,
            "dividends": dividends,
            "cash_movements": cash_movements,
            "positions": [],
            "fees": [],
        }

    def _build_transactions(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        transactions: list[
            dict[str, Any]
        ] = []

        for row in rows:
            ticker = row.get(
                "ticker",
                ""
            )

            transaction_type = str(
                row.get(
                    "transaction_type",
                    "",
                )
            ).upper()

            quantity = row.get(
                "quantity"
            )

            price = row.get(
                "price"
            )

            currency = str(
                row.get(
                    "currency",
                    "",
                )
            ).upper()

            transaction_date = row.get(
                "date"
            )

            commission = abs(
                float(
                    row.get(
                        "commission",
                        0,
                    )
                    or 0
                )
            )

            fx_rate = row.get(
                "fx_rate"
            )

            if fx_rate is not None:
                fx_rate = float(
                    fx_rate
                )

                if fx_rate <= 0:
                    raise ValueError(
                        f"Revolut {ticker} "
                        "transaction FX rate "
                        "must be greater than zero."
                    )

            if not ticker:
                raise ValueError(
                    "Revolut transaction "
                    "does not contain ticker."
                )

            if transaction_type not in {
                "BUY",
                "SELL",
            }:
                raise ValueError(
                    "Unsupported Revolut "
                    "transaction type: "
                    f"{transaction_type}."
                )

            if quantity is None:
                raise ValueError(
                    f"Revolut {ticker} "
                    "transaction does not "
                    "contain quantity."
                )

            quantity = abs(
                float(quantity)
            )

            if quantity <= 0:
                raise ValueError(
                    f"Revolut {ticker} "
                    "transaction quantity "
                    "must be greater than zero."
                )

            if price is None:
                raise ValueError(
                    f"Revolut {ticker} "
                    "transaction does not "
                    "contain price."
                )

            price = abs(
                float(price)
            )

            if not currency:
                raise ValueError(
                    f"Revolut {ticker} "
                    "transaction does not "
                    "contain currency."
                )

            broker_transaction_id = (
                self._build_transaction_id(
                    row
                )
            )

            transactions.append(
                {
                    "broker": "REVOLUT",
                    "ticker": ticker,
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
                    "fx_rate": fx_rate,
                    "transaction_date": (
                        transaction_date
                    ),
                    "asset": ticker,
                    "asset_type": "Stock",
                    "market_ticker": ticker,
                }
            )

        return transactions

    def _build_dividends(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        dividends: list[
            dict[str, Any]
        ] = []

        for row in rows:
            ticker = row.get(
                "ticker",
                ""
            )

            amount = row.get(
                "amount"
            )

            if not ticker:
                continue

            if amount is None:
                continue

            amount = float(
                amount
            )

            fx_rate = row.get(
                "fx_rate"
            )

            if fx_rate is not None:
                fx_rate = float(
                    fx_rate
                )

                if fx_rate <= 0:
                    raise ValueError(
                        f"Revolut {ticker} "
                        "dividend FX rate "
                        "must be greater than zero."
                    )

            original_type = str(
                row.get(
                    "original_type",
                    "DIVIDEND",
                )
            )

            dividends.append(
                {
                    "broker": "REVOLUT",
                    "ticker": ticker,
                    "payment_date": (
                        row.get("date")
                    ),
                    "gross_amount": amount,
                    "tax_amount": 0.0,
                    "net_amount": amount,
                    "currency": str(
                        row.get(
                            "currency",
                            "",
                        )
                    ).upper(),
                    "fx_rate": fx_rate,
                    "description": (
                        original_type
                    ),
                }
            )

        return dividends

    def _build_cash_movements(
        self,
        rows: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        cash_movements: list[
            dict[str, Any]
        ] = []

        for row in rows:
            amount = row.get(
                "amount"
            )

            if amount is None:
                continue

            movement_type = str(
                row.get(
                    "movement_type",
                    "",
                )
            ).upper()

            fx_rate = row.get(
                "fx_rate"
            )

            if fx_rate is not None:
                fx_rate = float(
                    fx_rate
                )

                if fx_rate <= 0:
                    raise ValueError(
                        "Revolut cash movement "
                        "FX rate must be "
                        "greater than zero."
                    )

            description_parts = [
                "Revolut",
                movement_type,
            ]

            ticker = row.get(
                "ticker"
            )

            if ticker:
                description_parts.append(
                    str(ticker)
                )

            cash_movements.append(
                {
                    "broker": "REVOLUT",
                    "movement_type": (
                        movement_type
                    ),
                    "amount": float(
                        amount
                    ),
                    "currency": str(
                        row.get(
                            "currency",
                            "",
                        )
                    ).upper(),
                    "fx_rate": fx_rate,
                    "movement_date": (
                        row.get("date")
                    ),
                    "description": " - ".join(
                        description_parts
                    ),
                }
            )

        return cash_movements

    def _build_transaction_id(
        self,
        row: dict[str, Any],
    ) -> str:
        identity = "|".join(
            [
                "REVOLUT",
                str(
                    row.get(
                        "date",
                        "",
                    )
                ),
                str(
                    row.get(
                        "ticker",
                        "",
                    )
                ),
                str(
                    row.get(
                        "transaction_type",
                        "",
                    )
                ),
                str(
                    row.get(
                        "quantity",
                        "",
                    )
                ),
                str(
                    row.get(
                        "price",
                        "",
                    )
                ),
                str(
                    row.get(
                        "commission",
                        "",
                    )
                ),
                str(
                    row.get(
                        "total_amount",
                        "",
                    )
                ),
                str(
                    row.get(
                        "currency",
                        "",
                    )
                ),
                str(
                    row.get(
                        "original_type",
                        "",
                    )
                ),
            ]
        )

        digest = hashlib.sha256(
            identity.encode("utf-8")
        ).hexdigest()

        return (
            f"REVOLUT-{digest}"
        )