from datetime import date
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


TransactionType = Literal[
    "BUY",
    "SELL",
    "REDEMPTION",
    "QUANTITY_ADJUSTMENT",
]


class TransactionCreate(BaseModel):
    investment_id: int = Field(
        gt=0,
    )

    broker_transaction_id: (
        str | None
    ) = None

    transaction_type: (
        TransactionType
    )

    quantity: float = Field(
        gt=0,
    )

    price: float = Field(
        ge=0,
    )

    currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=10,
    )

    transaction_date: date

    @model_validator(mode="after")
    def validate_price(self):
        if (
            self.transaction_type
            != "QUANTITY_ADJUSTMENT"
            and self.price <= 0
        ):
            raise ValueError(
                "Price must be greater "
                "than 0 for this "
                "transaction type."
            )

        return self


class TransactionResponse(
    TransactionCreate
):
    id: int

    realized_profit: float

    model_config = ConfigDict(
        from_attributes=True,
    )