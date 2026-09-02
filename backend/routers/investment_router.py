from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db

from schemas.investment import (
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentResponse,
)

from services.investment_service import (
    create_investment,
    get_investments,
    update_investment,
    delete_investment,
)


router = APIRouter(
    prefix="/investments",
    tags=["Investments"],
)


@router.post(
    "/",
    response_model=InvestmentResponse,
)
def add_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_investment(
            db,
            investment,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=list[InvestmentResponse],
)
def list_investments(
    db: Session = Depends(get_db),
):
    return get_investments(db)


@router.put(
    "/{investment_id}",
    response_model=InvestmentResponse,
)
def edit_investment(
    investment_id: int,
    investment: InvestmentUpdate,
    db: Session = Depends(get_db),
):
    try:
        result = update_investment(
            db,
            investment_id,
            investment,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Investment not found",
            )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.delete("/{investment_id}")
def remove_investment(
    investment_id: int,
    db: Session = Depends(get_db),
):
    result = delete_investment(
        db,
        investment_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Investment not found",
        )

    return result