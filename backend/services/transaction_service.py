from sqlalchemy.orm import Session

from models.transaction import Transaction
from schemas.transaction_schema import TransactionCreate


def get_transactions(db: Session):
    return db.query(Transaction).all()


def create_transaction(db: Session, transaction: TransactionCreate):
    new_transaction = Transaction(**transaction.model_dump())

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction