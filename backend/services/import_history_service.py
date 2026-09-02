from hashlib import sha256
from pathlib import Path

from sqlalchemy.orm import Session

from models.import_history import ImportHistory
from repositories import import_history_repository


def calculate_file_hash(
    file_path: str,
) -> str:
    hash_object = sha256()

    with open(
        file_path,
        "rb",
    ) as file:
        while True:
            chunk = file.read(8192)

            if not chunk:
                break

            hash_object.update(chunk)

    return hash_object.hexdigest()


def already_imported(
    db: Session,
    file_path: str,
) -> bool:
    file_hash = calculate_file_hash(
        file_path
    )

    return (
        import_history_repository.exists_by_file_hash(
            db,
            file_hash,
        )
    )


def create_history(
    db: Session,
    broker: str,
    file_path: str,
    preview: dict,
):
    file_hash = calculate_file_hash(
        file_path
    )

    history = ImportHistory(
        broker=broker,
        file_name=Path(file_path).name,
        file_hash=file_hash,
        transactions_count=preview.get(
            "transactions_count",
            0,
        ),
        dividends_count=preview.get(
            "dividends_count",
            0,
        ),
        cash_movements_count=preview.get(
            "cash_movements_count",
            0,
        ),
        positions_count=preview.get(
            "positions_count",
            0,
        ),
        duplicates_skipped=0,
        status="COMPLETED",
    )

    import_history_repository.add(
        db,
        history,
    )

    db.commit()

    db.refresh(history)

    return history


def get_history(
    db: Session,
):
    return (
        import_history_repository.get_all(
            db
        )
    )