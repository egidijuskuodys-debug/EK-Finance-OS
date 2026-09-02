from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db

from services.market_data_service import (
    get_current_price,
    update_all_prices,
)


router = APIRouter(
    prefix="/market",
    tags=["Market Data"],
)


@router.get("/price/{ticker}")
def get_price(ticker: str):
    price = get_current_price(ticker)

    if price is None:
        raise HTTPException(
            status_code=404,
            detail=f"Ticker '{ticker}' not found",
        )

    return {
        "ticker": ticker.upper(),
        "current_price": price,
    }


@router.post("/update-all")
def update_prices(
    db: Session = Depends(get_db),
):
    return update_all_prices(db)