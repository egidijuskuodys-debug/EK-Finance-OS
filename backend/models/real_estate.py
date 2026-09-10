from sqlalchemy import (
    Column,
    Date,
    Float,
    Integer,
    String,
)

from database.db import Base


class RealEstateProperty(Base):
    __tablename__ = (
        "real_estate_properties"
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    address = Column(
        String(250),
        nullable=True,
    )

    property_type = Column(
        String(50),
        nullable=False,
        default="Apartment",
    )

    purchase_price = Column(
        Float,
        nullable=False,
    )

    current_value = Column(
        Float,
        nullable=False,
    )

    down_payment = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    loan_original_amount = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    loan_balance = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    interest_rate = Column(
        Float,
        nullable=True,
    )

    monthly_payment = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    monthly_rent = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    monthly_expenses = Column(
        Float,
        nullable=False,
        default=0.0,
    )

    currency = Column(
        String(10),
        nullable=False,
        default="EUR",
    )

    purchase_date = Column(
        Date,
        nullable=True,
    )

    loan_end_date = Column(
        Date,
        nullable=True,
    )