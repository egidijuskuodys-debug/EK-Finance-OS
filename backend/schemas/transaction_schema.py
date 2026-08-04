from pydantic import BaseModel
from datetime import date


class TransactionCreate(BaseModel):
    investment_id: int
    transaction_type: str
    quantity: float
    price: float
    currency: str = "EUR"
    transaction_date: date


class TransactionResponse(TransactionCreate):
    id: int

    class Config:
        from_attributes = True