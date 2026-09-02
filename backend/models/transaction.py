from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    investment_id = Column(
        Integer,
        ForeignKey("investments.id"),
        nullable=False,
        index=True,
    )

    broker_transaction_id = Column(
        String(100),
        nullable=True,
        unique=True,
        index=True,
    )

    transaction_type = Column(
        String(20),
        nullable=False,
    )

    quantity = Column(
        Float,
        nullable=False,
    )

    price = Column(
        Float,
        nullable=False,
    )

    commission = Column(
        Float,
        nullable=False,
        default=0,
    )

    realized_profit = Column(
        Float,
        nullable=False,
        default=0,
    )

    currency = Column(
        String(10),
        default="EUR",
    )

    fx_rate = Column(
        Float,
        nullable=True,
    )

    transaction_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    investment = relationship(
        "Investment",
        back_populates="transactions",
    )