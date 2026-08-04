from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.transaction_schema import (
    TransactionCreate,
    TransactionResponse,
)
from services.transaction_service import (
    get_transactions,
    create_transaction,
)

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)


@router.get("/", response_model=list[TransactionResponse])
def read_transactions(db: Session = Depends(get_db)):
    return get_transactions(db)


@router.post("/", response_model=TransactionResponse)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
):
    return create_transaction(db, transaction)