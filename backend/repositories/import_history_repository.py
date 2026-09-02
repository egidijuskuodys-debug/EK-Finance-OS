from sqlalchemy.orm import Session

from models.import_history import ImportHistory


def get_all(db: Session):
    return (
        db.query(ImportHistory)
        .order_by(
            ImportHistory.imported_at.desc(),
            ImportHistory.id.desc(),
        )
        .all()
    )


def get_by_id(
    db: Session,
    import_id: int,
):
    return (
        db.query(ImportHistory)
        .filter(
            ImportHistory.id == import_id
        )
        .first()
    )


def get_by_file_hash(
    db: Session,
    file_hash: str,
):
    return (
        db.query(ImportHistory)
        .filter(
            ImportHistory.file_hash == file_hash
        )
        .first()
    )


def exists_by_file_hash(
    db: Session,
    file_hash: str,
) -> bool:
    return (
        db.query(ImportHistory)
        .filter(
            ImportHistory.file_hash == file_hash
        )
        .first()
        is not None
    )


def add(
    db: Session,
    import_history: ImportHistory,
):
    db.add(import_history)
    db.flush()

    return import_history


def update(
    db: Session,
    import_history: ImportHistory,
):
    db.flush()

    return import_history


def delete(
    db: Session,
    import_history: ImportHistory,
):
    db.delete(import_history)
    db.flush()

    return True