from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    investment_id: int = Field(gt=0)

    broker_transaction_id: str | None = None

    transaction_type: Literal[
        "BUY",
        "SELL",
    ]

    quantity: float = Field(gt=0)

    price: float = Field(gt=0)

    currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=10,
    )

    transaction_date: date


class TransactionResponse(TransactionCreate):
    id: int

    realized_profit: float

    model_config = ConfigDict(
        from_attributes=True,
    )