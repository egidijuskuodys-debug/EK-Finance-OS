from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ImportContext:
    broker: str
    file_path: Path

    transactions: list[dict[str, Any]] = field(
        default_factory=list
    )

    dividends: list[dict[str, Any]] = field(
        default_factory=list
    )

    cash_movements: list[dict[str, Any]] = field(
        default_factory=list
    )

    positions: list[dict[str, Any]] = field(
        default_factory=list
    )

    fees: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    @property
    def file_name(self) -> str:
        return self.file_path.name

    @property
    def transactions_count(self) -> int:
        return len(self.transactions)

    @property
    def dividends_count(self) -> int:
        return len(self.dividends)

    @property
    def cash_movements_count(self) -> int:
        return len(self.cash_movements)

    @property
    def positions_count(self) -> int:
        return len(self.positions)

    @property
    def fees_count(self) -> int:
        return len(self.fees)

    def to_data_dict(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        return {
            "transactions": self.transactions,
            "dividends": self.dividends,
            "cash_movements": self.cash_movements,
            "positions": self.positions,
            "fees": self.fees,
        }

    def to_preview_dict(
        self,
    ) -> dict[str, Any]:
        return {
            "broker": self.broker,
            "file_name": self.file_name,
            "transactions_count": (
                self.transactions_count
            ),
            "dividends_count": (
                self.dividends_count
            ),
            "cash_movements_count": (
                self.cash_movements_count
            ),
            "positions_count": (
                self.positions_count
            ),
            "fees_count": self.fees_count,
            "metadata": self.metadata,
            "data": self.to_data_dict(),
        }