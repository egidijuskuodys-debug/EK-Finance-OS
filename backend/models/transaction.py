from sqlalchemy import Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    investment_id = Column(Integer, ForeignKey("investments.id"), nullable=False)

    transaction_type = Column(String(20), nullable=False)

    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    currency = Column(String(10), default="EUR")

    transaction_date = Column(Date)

    investment = relationship(
        "Investment",
        back_populates="transactions"
    )