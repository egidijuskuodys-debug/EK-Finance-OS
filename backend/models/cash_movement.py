from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    String,
)

from database.db import Base


class CashMovement(Base):
    __tablename__ = "cash_movements"

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

    movement_type = Column(
        String(20),
        nullable=False,
    )

    amount = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
    )

    movement_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    description = Column(
        String(500),
        nullable=True,
    )

    broker_movement_id = Column(
        String(64),
        nullable=True,
        unique=True,
        index=True,
    )