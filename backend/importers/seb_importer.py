from typing import Any

from importers.base_importer import BaseImporter
from importers.seb.ocr_reader import (
    read_seb_pdf_ocr,
)
from importers.seb.parser import (
    parse_seb_ocr_pages,
)


class SEBImporter(BaseImporter):
    SUPPORTED_EXTENSIONS = {
        ".pdf",
    }

    def __init__(
        self,
        file_path: str,
    ):
        super().__init__(
            file_path
        )

        self._pages: (
            list[str] | None
        ) = None

        self._parsed_data: (
            dict[
                str,
                list[
                    dict[str, Any]
                ],
            ]
            | None
        ) = None

    def get_broker_name(
        self,
    ) -> str:
        return "SEB"

    def _read_pages(
        self,
    ) -> list[str]:
        if self._pages is None:
            self._pages = (
                read_seb_pdf_ocr(
                    self.file_path
                )
            )

        return self._pages

    def validate_structure(
        self,
    ) -> None:
        pages = self._read_pages()

        text = "\n".join(
            pages
        )

        normalized_text = (
            " ".join(
                text.lower().split()
            )
        )

        required_markers = [
            "pasirinktas laikotarpis",
            "vertybinių popierių sąskaita",
        ]

        if not all(
            marker in normalized_text
            for marker in required_markers
        ):
            raise ValueError(
                "PDF does not appear "
                "to be a valid SEB "
                "securities statement."
            )

        has_transaction_table = all(
            marker in normalized_text
            for marker in [
                "vertybinių popierių pavadinimas",
                "pavedimo tipo kodas",
                "kaina",
                "kiekis",
                "suma",
            ]
        )

        has_no_transactions = (
            "vertybinių popierių "
            "sandorių nebuvo"
            in normalized_text
        )

        if (
            not has_transaction_table
            and not has_no_transactions
        ):
            raise ValueError(
                "SEB securities "
                "statement structure "
                "was not recognized."
            )

    def parse(
        self,
    ) -> dict[
        str,
        list[
            dict[str, Any]
        ],
    ]:
        if self._parsed_data is None:
            self._parsed_data = (
                parse_seb_ocr_pages(
                    self._read_pages()
                )
            )

        return self._parsed_data

    def get_metadata(
        self,
    ) -> dict[str, Any]:
        pages = self._read_pages()

        text = "\n".join(
            pages
        )

        normalized_text = (
            " ".join(
                text.lower().split()
            )
        )

        return {
            "source_type": (
                "SEB_SECURITIES_STATEMENT"
            ),
            "source_format": "PDF",
            "ocr": True,
            "page_count": len(
                pages
            ),
            "contains_transactions": (
                "vertybinių popierių pavadinimas"
                in normalized_text
            ),
        }