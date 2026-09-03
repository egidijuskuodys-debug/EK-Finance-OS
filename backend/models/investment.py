from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from database.db import Base


class Investment(Base):
    __tablename__ = "investments"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    broker = Column(
        String(100),
        nullable=False,
    )

    asset = Column(
        String(100),
        nullable=False,
    )

    # Trumpas simbolis vartotojui
    ticker = Column(
        String(20),
        nullable=False,
    )

    # Simbolis rinkos duomenu tiekejui
    # (Yahoo Finance)
    market_ticker = Column(
        String(30),
        nullable=False,
    )

    asset_type = Column(
        String(50),
        nullable=False,
    )

    quantity = Column(
        Float,
        nullable=False,
    )

    purchase_price = Column(
        Float,
        nullable=False,
    )

    current_price = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String(10),
        default="EUR",
    )

    purchase_date = Column(
        Date,
    )

    transactions = relationship(
        "Transaction",
        back_populates="investment",
        cascade="all, delete-orphan",
    )

    dividends = relationship(
        "Dividend",
        back_populates="investment",
        cascade="all, delete-orphan",
    )

    price_history = relationship(
        "PriceHistory",
        back_populates="investment",
        cascade="all, delete-orphan",
        order_by="PriceHistory.price_date",
    )