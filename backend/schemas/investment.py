from datetime import date
from pydantic import BaseModel


class InvestmentCreate(BaseModel):
    broker: str
    asset: str
    ticker: str
    quantity: float
    purchase_price: float
    currency: str = "EUR"
    purchase_date: date


class InvestmentResponse(InvestmentCreate):
    id: int

    class Config:
        from_attributes = True