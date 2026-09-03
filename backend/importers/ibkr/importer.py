from typing import Any

from importers.base_importer import BaseImporter
from importers.ibkr.cash_parser import (
    parse_cash_movements,
)
from importers.ibkr.dividends_parser import (
    parse_dividends,
)
from importers.ibkr.positions_parser import (
    parse_positions,
)
from importers.ibkr.section_reader import (
    read_ibkr_file,
)
from importers.ibkr.trades_parser import (
    parse_forex_cash_movements,
    parse_trades,
)


class IBKRImporter(BaseImporter):
    REQUIRED_SECTIONS = {
        "Trades",
        "Open Positions",
    }

    def __init__(
        self,
        file_path: str,
    ):
        super().__init__(file_path)

        self.sections: dict[
            str,
            list[dict[str, Any]],
        ] = {}

        self.metadata: dict[
            str,
            Any,
        ] = {}

    def get_broker_name(self) -> str:
        return "Interactive Brokers"

    def validate_structure(self) -> None:
        (
            self.sections,
            self.metadata,
        ) = read_ibkr_file(
            self.file_path
        )

        missing_sections = (
            self.REQUIRED_SECTIONS
            - set(self.sections.keys())
        )

        if missing_sections:
            missing = ", ".join(
                sorted(missing_sections)
            )

            raise ValueError(
                "IBKR CSV is missing required "
                f"sections: {missing}."
            )

    def get_metadata(
        self,
    ) -> dict[str, Any]:
        return self.metadata.copy()

    def parse(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        if not self.sections:
            (
                self.sections,
                self.metadata,
            ) = read_ibkr_file(
                self.file_path
            )

        trade_records = self.sections.get(
            "Trades",
            [],
        )

        transactions = parse_trades(
            trade_records
        )

        forex_cash_movements = (
            parse_forex_cash_movements(
                trade_records
            )
        )

        dividends = parse_dividends(
            self.sections.get(
                "Dividends",
                [],
            )
        )

        cash_movements = (
            parse_cash_movements(
                self.sections.get(
                    "Deposits & Withdrawals",
                    [],
                )
            )
        )

        cash_movements.extend(
            forex_cash_movements
        )

        positions = parse_positions(
            self.sections.get(
                "Open Positions",
                [],
            )
        )

        return {
            "transactions": transactions,
            "dividends": dividends,
            "cash_movements": cash_movements,
            "positions": positions,
            "fees": [],
        }

    def preview(
        self,
    ) -> dict[str, Any]:
        preview_data = super().preview()

        preview_data[
            "detected_sections"
        ] = sorted(
            self.sections.keys()
        )

        return preview_data