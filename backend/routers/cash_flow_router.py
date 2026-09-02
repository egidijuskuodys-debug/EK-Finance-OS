from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from database.db import get_db
from services.cash_flow_service import (
    get_cash_flow_by_broker,
    get_cash_flow_by_year,
    get_cash_flow_summary,
)


router = APIRouter()


@router.get("/summary")
def cash_flow_summary(
    db: Session = Depends(get_db),
):
    return get_cash_flow_summary(
        db
    )


@router.get("/by-broker")
def cash_flow_by_broker(
    db: Session = Depends(get_db),
):
    return get_cash_flow_by_broker(
        db
    )


@router.get("/by-year")
def cash_flow_by_year(
    db: Session = Depends(get_db),
):
    return get_cash_flow_by_year(
        db
    )