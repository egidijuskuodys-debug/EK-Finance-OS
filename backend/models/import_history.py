from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from database.db import Base


class ImportHistory(Base):
    __tablename__ = "import_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    broker = Column(
        String(100),
        nullable=False,
        index=True,
    )

    file_name = Column(
        String(255),
        nullable=False,
    )

    file_hash = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
    )

    imported_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True,
    )

    transactions_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    dividends_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    cash_movements_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    positions_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    duplicates_skipped = Column(
        Integer,
        nullable=False,
        default=0,
    )

    status = Column(
        String(50),
        nullable=False,
        default="COMPLETED",
    )

    error_message = Column(
        String(1000),
        nullable=True,
    )