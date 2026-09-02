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


class Dividend(Base):
    __tablename__ = "dividends"

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

    broker_dividend_id = Column(
        String(64),
        nullable=True,
        unique=True,
        index=True,
    )

    payment_date = Column(
        Date,
        nullable=False,
        index=True,
    )

    gross_amount = Column(
        Float,
        nullable=False,
    )

    tax_amount = Column(
        Float,
        nullable=False,
        default=0,
    )

    net_amount = Column(
        Float,
        nullable=False,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="EUR",
    )

    fx_rate = Column(
        Float,
        nullable=True,
    )

    notes = Column(
        String(500),
        nullable=True,
    )

    investment = relationship(
        "Investment",
        back_populates="dividends",
    )