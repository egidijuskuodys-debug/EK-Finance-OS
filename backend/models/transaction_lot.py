from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
)
from sqlalchemy.orm import relationship

from database.db import Base


class TransactionLot(Base):
    __tablename__ = "transaction_lots"

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

    buy_transaction_id = Column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    original_quantity = Column(
        Float,
        nullable=False,
    )

    remaining_quantity = Column(
        Float,
        nullable=False,
    )

    purchase_price = Column(
        Float,
        nullable=False,
    )

    purchase_date = Column(
        Date,
        nullable=False,
    )

    investment = relationship(
        "Investment",
    )

    buy_transaction = relationship(
        "Transaction",
    )