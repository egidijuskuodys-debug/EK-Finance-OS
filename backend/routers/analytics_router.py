from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db

from services.analytics_service import (
    get_allocation,
    get_dividend_summary,
    get_dividends_by_investment,
    get_dividends_by_year,
    get_performance,
    get_summary,
    recalculate_portfolio,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def portfolio_summary(
    db: Session = Depends(get_db),
):
    return get_summary(db)


@router.get("/allocation")
def portfolio_allocation(
    db: Session = Depends(get_db),
):
    return get_allocation(db)


@router.get("/performance")
def portfolio_performance(
    db: Session = Depends(get_db),
):
    return get_performance(db)


@router.get("/dividends/summary")
def dividend_summary(
    db: Session = Depends(get_db),
):
    return get_dividend_summary(db)


@router.get("/dividends/by-year")
def dividends_by_year(
    db: Session = Depends(get_db),
):
    return get_dividends_by_year(db)


@router.get("/dividends/by-investment")
def dividends_by_investment(
    db: Session = Depends(get_db),
):
    return get_dividends_by_investment(db)


@router.post("/recalculate")
def recalculate(
    db: Session = Depends(get_db),
):
    return recalculate_portfolio(db)