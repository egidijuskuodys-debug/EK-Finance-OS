from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from importers.import_context import ImportContext


class BaseImporter(ABC):
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._context: ImportContext | None = None

    def validate_file(self) -> None:
        if not self.file_path.exists():
            raise ValueError(
                f"Import file not found: {self.file_path}"
            )

        if not self.file_path.is_file():
            raise ValueError(
                "Import path must point to a file."
            )

        if self.file_path.suffix.lower() != ".csv":
            raise ValueError(
                "Only CSV files are currently supported."
            )

        if self.file_path.stat().st_size == 0:
            raise ValueError(
                "Import file is empty."
            )

    @abstractmethod
    def validate_structure(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def parse(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        raise NotImplementedError

    @abstractmethod
    def get_broker_name(self) -> str:
        raise NotImplementedError

    def get_metadata(
        self,
    ) -> dict[str, Any]:
        return {}

    def build_context(self) -> ImportContext:
        if self._context is not None:
            return self._context

        self.validate_file()
        self.validate_structure()

        parsed_data = self.parse()

        self._context = ImportContext(
            broker=self.get_broker_name(),
            file_path=self.file_path,
            transactions=parsed_data.get(
                "transactions",
                [],
            ),
            dividends=parsed_data.get(
                "dividends",
                [],
            ),
            cash_movements=parsed_data.get(
                "cash_movements",
                [],
            ),
            positions=parsed_data.get(
                "positions",
                [],
            ),
            fees=parsed_data.get(
                "fees",
                [],
            ),
            metadata=self.get_metadata(),
        )

        return self._context

    def preview(self) -> dict[str, Any]:
        context = self.build_context()

        return context.to_preview_dict()