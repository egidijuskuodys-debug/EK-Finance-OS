from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db

from schemas.dividend_schema import (
    DividendCreate,
    DividendResponse,
    DividendUpdate,
)

from services.dividend_service import (
    create_dividend,
    delete_dividend,
    get_dividend_by_id,
    get_dividends,
    get_dividends_by_investment,
    update_dividend,
)


router = APIRouter(
    prefix="/dividends",
    tags=["Dividends"],
)


@router.get(
    "/",
    response_model=list[DividendResponse],
)
def list_dividends(
    db: Session = Depends(get_db),
):
    return get_dividends(db)


@router.get(
    "/{dividend_id}",
    response_model=DividendResponse,
)
def read_dividend(
    dividend_id: int,
    db: Session = Depends(get_db),
):
    dividend = get_dividend_by_id(
        db,
        dividend_id,
    )

    if dividend is None:
        raise HTTPException(
            status_code=404,
            detail="Dividend not found",
        )

    return dividend


@router.get(
    "/investment/{investment_id}",
    response_model=list[DividendResponse],
)
def list_investment_dividends(
    investment_id: int,
    db: Session = Depends(get_db),
):
    try:
        return get_dividends_by_investment(
            db,
            investment_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.post(
    "/",
    response_model=DividendResponse,
)
def add_dividend(
    dividend: DividendCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_dividend(
            db,
            dividend,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.put(
    "/{dividend_id}",
    response_model=DividendResponse,
)
def edit_dividend(
    dividend_id: int,
    dividend: DividendUpdate,
    db: Session = Depends(get_db),
):
    try:
        result = update_dividend(
            db,
            dividend_id,
            dividend,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Dividend not found",
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.delete("/{dividend_id}")
def remove_dividend(
    dividend_id: int,
    db: Session = Depends(get_db),
):
    result = delete_dividend(
        db,
        dividend_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Dividend not found",
        )

    return result