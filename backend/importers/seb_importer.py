from typing import Any

from importers.base_importer import BaseImporter


class SEBImporter(BaseImporter):
    def validate_structure(self) -> None:
        raise NotImplementedError(
            "SEB CSV structure validation "
            "is not implemented yet."
        )

    def parse(
        self,
    ) -> dict[str, list[dict[str, Any]]]:
        raise NotImplementedError(
            "SEB CSV parsing is not implemented yet."
        )