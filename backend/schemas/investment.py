from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class InvestmentBase(BaseModel):
    broker: str
    asset: str
    ticker: str
    market_ticker: str
    asset_type: str
    quantity: float
    purchase_price: float
    current_price: float
    currency: str = "EUR"
    purchase_date: Optional[date] = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentUpdate(BaseModel):
    broker: Optional[str] = None
    asset: Optional[str] = None
    ticker: Optional[str] = None
    market_ticker: Optional[str] = None
    asset_type: Optional[str] = None
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    currency: Optional[str] = None
    purchase_date: Optional[date] = None


class InvestmentResponse(InvestmentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)