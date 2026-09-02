from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db

from schemas.transaction_schema import (
    TransactionCreate,
    TransactionResponse,
)

from services.transaction_service import (
    get_transactions,
    create_transaction,
    delete_transaction,
)


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get(
    "/",
    response_model=list[TransactionResponse],
)
def read_transactions(
    db: Session = Depends(get_db),
):
    return get_transactions(db)


@router.post(
    "/",
    response_model=TransactionResponse,
)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_transaction(
            db,
            transaction,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.delete("/{transaction_id}")
def remove_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
):
    try:
        result = delete_transaction(
            db,
            transaction_id,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Transaction not found",
            )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error