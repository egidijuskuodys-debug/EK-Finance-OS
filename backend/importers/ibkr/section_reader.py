import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def parse_statement_period(
    value: str,
) -> tuple[Any, Any]:
    value = value.strip()

    if " - " not in value:
        return None, None

    start_text, end_text = value.split(
        " - ",
        maxsplit=1,
    )

    try:
        start_date = datetime.strptime(
            start_text.strip(),
            "%B %d, %Y",
        ).date()

        end_date = datetime.strptime(
            end_text.strip(),
            "%B %d, %Y",
        ).date()

    except ValueError:
        return None, None

    return start_date, end_date


def read_ibkr_file(
    file_path: str | Path,
) -> tuple[
    dict[str, list[dict[str, Any]]],
    dict[str, Any],
]:
    path = Path(file_path)

    if not path.exists():
        raise ValueError(
            "IBKR CSV file not found."
        )

    sections: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(list)

    headers: dict[
        str,
        list[str],
    ] = {}

    metadata: dict[str, Any] = {
        "statement_title": None,
        "period": None,
        "period_start": None,
        "period_end": None,
        "generated_at": None,
    }

    with path.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.reader(file)

        for row_number, row in enumerate(
            reader,
            start=1,
        ):
            if len(row) < 2:
                continue

            section_name = row[0].strip()
            row_type = row[1].strip()

            if not section_name:
                continue

            # Sąmoningai ignoruojame jautrią
            # Account Information sekciją.
            if section_name == "Account Information":
                continue

            if row_type == "Header":
                headers[section_name] = [
                    value.strip()
                    for value in row[2:]
                ]

                continue

            if row_type != "Data":
                continue

            section_headers = headers.get(
                section_name
            )

            if not section_headers:
                continue

            values = row[2:]

            record = {
                header: (
                    values[index].strip()
                    if index < len(values)
                    else ""
                )
                for index, header in enumerate(
                    section_headers
                )
            }

            record["_row_number"] = (
                row_number
            )

            sections[
                section_name
            ].append(
                record
            )

            if section_name == "Statement":
                field_name = record.get(
                    "Field Name",
                    "",
                )

                field_value = record.get(
                    "Field Value",
                    "",
                )

                if field_name == "Title":
                    metadata[
                        "statement_title"
                    ] = field_value

                elif field_name == "Period":
                    metadata[
                        "period"
                    ] = field_value

                    (
                        period_start,
                        period_end,
                    ) = parse_statement_period(
                        field_value
                    )

                    metadata[
                        "period_start"
                    ] = period_start

                    metadata[
                        "period_end"
                    ] = period_end

                elif field_name == "WhenGenerated":
                    metadata[
                        "generated_at"
                    ] = field_value

    return (
        dict(sections),
        metadata,
    )


def read_ibkr_sections(
    file_path: str | Path,
) -> dict[str, list[dict[str, Any]]]:
    sections, _ = read_ibkr_file(
        file_path
    )

    return sections