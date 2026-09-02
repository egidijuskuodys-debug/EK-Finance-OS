from typing import Any

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


def load_contexts(
    broker: str,
    file_paths: list[str],
):
    contexts = []

    for file_path in file_paths:
        importer = ImporterFactory.get_importer(
            broker=broker,
            file_path=file_path,
        )

        context = importer.build_context()

        contexts.append(context)

    for context in contexts:
        if context.metadata.get(
            "period_start"
        ) is None:
            raise ValueError(
                f"Statement period could not be "
                f"determined for {context.file_name}."
            )

    contexts.sort(
        key=lambda context: (
            context.metadata["period_start"]
        )
    )

    return contexts


def preview_multiple_files(
    broker: str,
    file_paths: list[str],
) -> dict[str, Any]:
    contexts = load_contexts(
        broker=broker,
        file_paths=file_paths,
    )

    files = []

    total_transactions = 0
    total_dividends = 0
    total_cash_movements = 0
    total_positions = 0

    previous_end = None

    warnings = []

    for context in contexts:
        period_start = context.metadata.get(
            "period_start"
        )

        period_end = context.metadata.get(
            "period_end"
        )

        if (
            previous_end is not None
            and period_start is not None
        ):
            days_between = (
                period_start
                - previous_end
            ).days

            if days_between > 1:
                warnings.append(
                    {
                        "type": "PERIOD_GAP",
                        "previous_end": (
                            previous_end
                        ),
                        "next_start": (
                            period_start
                        ),
                        "days": (
                            days_between - 1
                        ),
                    }
                )

            elif days_between < 0:
                warnings.append(
                    {
                        "type": "PERIOD_OVERLAP",
                        "previous_end": (
                            previous_end
                        ),
                        "next_start": (
                            period_start
                        ),
                        "days": abs(
                            days_between
                        ),
                    }
                )

        if period_end is not None:
            previous_end = period_end

        files.append(
            {
                "file_name": context.file_name,
                "period_start": period_start,
                "period_end": period_end,
                "transactions": (
                    context.transactions_count
                ),
                "dividends": (
                    context.dividends_count
                ),
                "cash_movements": (
                    context.cash_movements_count
                ),
                "positions": (
                    context.positions_count
                ),
            }
        )

        total_transactions += (
            context.transactions_count
        )

        total_dividends += (
            context.dividends_count
        )

        total_cash_movements += (
            context.cash_movements_count
        )

        total_positions += (
            context.positions_count
        )

    return {
        "ready": len(warnings) == 0,
        "broker": broker,
        "files_count": len(contexts),
        "files": files,
        "totals": {
            "transactions": (
                total_transactions
            ),
            "dividends": (
                total_dividends
            ),
            "cash_movements": (
                total_cash_movements
            ),
            "positions": (
                total_positions
            ),
        },
        "warnings": warnings,
    }


def import_multiple_files(
    db: Session,
    broker: str,
    file_paths: list[str],
) -> dict[str, Any]:
    contexts = load_contexts(
        broker=broker,
        file_paths=file_paths,
    )

    imported_files = []
    skipped_files = []

    totals = {
        "investments_created": 0,
        "investments_existing": 0,
        "transactions_imported": 0,
        "transactions_skipped": 0,
        "dividends_imported": 0,
        "dividends_skipped": 0,
        "cash_movements_imported": 0,
        "cash_movements_skipped": 0,
    }

    try:
        for context in contexts:
            file_path = str(
                context.file_path
            )

            if already_imported(
                db,
                file_path,
            ):
                skipped_files.append(
                    {
                        "file_name": (
                            context.file_name
                        ),
                        "reason": (
                            "already_imported"
                        ),
                    }
                )

                continue

            investment_result = ensure_investments(
                db=db,
                positions=context.positions,
                transactions=context.transactions,
            )

            transaction_result = import_transactions(
                db=db,
                transactions=context.transactions,
            )

            dividend_result = import_dividends(
                db=db,
                dividends=context.dividends,
            )

            cash_result = import_cash_movements(
                db=db,
                cash_movements=(
                    context.cash_movements
                ),
            )

            history = create_import_history(
                db=db,
                broker=broker,
                file_path=file_path,
                transaction_result=(
                    transaction_result
                ),
                dividend_result=(
                    dividend_result
                ),
                cash_result=cash_result,
                positions_count=(
                    context.positions_count
                ),
            )

            imported_files.append(
                {
                    "file_name": (
                        context.file_name
                    ),
                    "period_start": (
                        context.metadata.get(
                            "period_start"
                        )
                    ),
                    "period_end": (
                        context.metadata.get(
                            "period_end"
                        )
                    ),
                    "import_history_id": (
                        history.id
                    ),
                }
            )

            totals[
                "investments_created"
            ] += investment_result[
                "created"
            ]

            totals[
                "investments_existing"
            ] += investment_result[
                "existing"
            ]

            totals[
                "transactions_imported"
            ] += transaction_result[
                "imported"
            ]

            totals[
                "transactions_skipped"
            ] += transaction_result[
                "skipped"
            ]

            totals[
                "dividends_imported"
            ] += dividend_result[
                "imported"
            ]

            totals[
                "dividends_skipped"
            ] += dividend_result[
                "skipped"
            ]

            totals[
                "cash_movements_imported"
            ] += cash_result[
                "imported"
            ]

            totals[
                "cash_movements_skipped"
            ] += cash_result[
                "skipped"
            ]

        db.commit()

        return {
            "success": True,
            "message": (
                "Multiple-file import "
                "completed successfully."
            ),
            "files_received": len(
                file_paths
            ),
            "files_imported": len(
                imported_files
            ),
            "files_skipped": len(
                skipped_files
            ),
            "imported_files": (
                imported_files
            ),
            "skipped_files": (
                skipped_files
            ),
            "totals": totals,
        }

    except Exception:
        db.rollback()
        raise