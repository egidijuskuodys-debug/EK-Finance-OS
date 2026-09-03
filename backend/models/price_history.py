from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from database.db import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    investment_id = Column(
        Integer,
        ForeignKey(
            "investments.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    market_ticker = Column(
        String(30),
        nullable=False,
        index=True,
    )

    price_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    close_price = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="EUR",
    )

    investment = relationship(
        "Investment",
        back_populates="price_history",
    )

    __table_args__ = (
        UniqueConstraint(
            "investment_id",
            "price_date",
            name=(
                "uq_price_history_"
                "investment_date"
            ),
        ),
    )