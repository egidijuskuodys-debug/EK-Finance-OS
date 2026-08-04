from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.investment import InvestmentCreate, InvestmentResponse
from services.investment_service import (
    create_investment,
    get_investments,
    delete_investment,
)

router = APIRouter()


@router.post("/", response_model=InvestmentResponse)
def add_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
):
    return create_investment(db, investment)


@router.get("/", response_model=list[InvestmentResponse])
def list_investments(
    db: Session = Depends(get_db),
):
    return get_investments(db)


@router.delete("/{investment_id}")
def remove_investment(
    investment_id: int,
    db: Session = Depends(get_db),
):
    result = delete_investment(db, investment_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investment not found"
        )

    return result