from pathlib import Path

from sqlalchemy.orm import Session

from models.import_history import ImportHistory
from repositories import import_history_repository
from services.import_history_service import (
    calculate_file_hash,
)


def create_import_history(
    db: Session,
    broker: str,
    file_path: str,
    transaction_result: dict[str, int],
    dividend_result: dict[str, int],
    cash_result: dict[str, int],
    positions_count: int,
    original_file_name: str | None = None,
) -> ImportHistory:
    file_hash = calculate_file_hash(
        file_path
    )

    duplicates_skipped = (
        transaction_result.get(
            "skipped",
            0,
        )
        + dividend_result.get(
            "skipped",
            0,
        )
        + cash_result.get(
            "skipped",
            0,
        )
    )

    file_name = (
        original_file_name
        if original_file_name
        else Path(
            file_path
        ).name
    )

    history = ImportHistory(
        broker=broker,
        file_name=file_name,
        file_hash=file_hash,
        transactions_count=(
            transaction_result.get(
                "imported",
                0,
            )
        ),
        dividends_count=(
            dividend_result.get(
                "imported",
                0,
            )
        ),
        cash_movements_count=(
            cash_result.get(
                "imported",
                0,
            )
        ),
        positions_count=positions_count,
        duplicates_skipped=(
            duplicates_skipped
        ),
        status="COMPLETED",
        error_message=None,
    )

    import_history_repository.add(
        db,
        history,
    )

    return history