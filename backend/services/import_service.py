from sqlalchemy.orm import Session

from importers.factory import ImporterFactory
from services.import_engine.cash_movement_importer import (
    import_cash_movements,
)
from services.import_engine.dividend_importer import (
    import_dividends,
)
from services.import_engine.import_history_manager import (
    create_import_history,
)
from services.import_engine.investment_importer import (
    ensure_investments,
)
from services.import_engine.transaction_importer import (
    import_transactions,
)
from services.import_history_service import (
    already_imported,
)


def preview_import(
    db: Session,
    broker: str,
    file_path: str,
):
    importer = ImporterFactory.get_importer(
        broker=broker,
        file_path=file_path,
    )

    return importer.preview()


def validate_import(
    db: Session,
    broker: str,
    file_path: str,
):
    if already_imported(
        db,
        file_path,
    ):
        return {
            "ready": False,
            "already_imported": True,
            "message": (
                "This file has already been imported."
            ),
        }

    importer = ImporterFactory.get_importer(
        broker=broker,
        file_path=file_path,
    )

    preview = importer.preview()

    return {
        "ready": True,
        "already_imported": False,
        "message": (
            "Import validation passed."
        ),
        "summary": {
            "transactions": preview.get(
                "transactions_count",
                0,
            ),
            "dividends": preview.get(
                "dividends_count",
                0,
            ),
            "cash_movements": preview.get(
                "cash_movements_count",
                0,
            ),
            "positions": preview.get(
                "positions_count",
                0,
            ),
        },
        "preview": preview,
    }


def import_file(
    db: Session,
    broker: str,
    file_path: str,
    original_file_name: str | None = None,
):
    if already_imported(
        db,
        file_path,
    ):
        return {
            "success": False,
            "already_imported": True,
            "message": (
                "This file has already been imported."
            ),
        }

    importer = ImporterFactory.get_importer(
        broker=broker,
        file_path=file_path,
    )

    preview = importer.preview()

    data = preview.get(
        "data",
        {},
    )

    positions = data.get(
        "positions",
        [],
    )

    transactions = data.get(
        "transactions",
        [],
    )

    dividends = data.get(
        "dividends",
        [],
    )

    cash_movements = data.get(
        "cash_movements",
        [],
    )

    try:
        investment_result = ensure_investments(
            db=db,
            positions=positions,
            transactions=transactions,
        )

        transaction_result = import_transactions(
            db=db,
            transactions=transactions,
        )

        dividend_result = import_dividends(
            db=db,
            dividends=dividends,
        )

        cash_result = import_cash_movements(
            db=db,
            cash_movements=cash_movements,
        )

        history = create_import_history(
            db=db,
            broker=broker,
            file_path=file_path,
            transaction_result=transaction_result,
            dividend_result=dividend_result,
            cash_result=cash_result,
            positions_count=len(
                positions
            ),
            original_file_name=(
                original_file_name
            ),
        )

        db.commit()

        db.refresh(history)

        return {
            "success": True,
            "already_imported": False,
            "message": (
                "Import completed successfully."
            ),
            "import_history_id": history.id,
            "file_name": history.file_name,
            "investments": {
                "created": (
                    investment_result[
                        "created"
                    ]
                ),
                "existing": (
                    investment_result[
                        "existing"
                    ]
                ),
            },
            "transactions": {
                "imported": (
                    transaction_result[
                        "imported"
                    ]
                ),
                "skipped": (
                    transaction_result[
                        "skipped"
                    ]
                ),
            },
            "dividends": {
                "imported": (
                    dividend_result[
                        "imported"
                    ]
                ),
                "skipped": (
                    dividend_result[
                        "skipped"
                    ]
                ),
            },
            "cash_movements": {
                "imported": (
                    cash_result[
                        "imported"
                    ]
                ),
                "skipped": (
                    cash_result[
                        "skipped"
                    ]
                ),
            },
            "positions_in_statement": len(
                positions
            ),
        }

    except Exception:
        db.rollback()
        raise