from sqlalchemy.orm import Session

from models.transaction import Transaction


def get_all(db: Session):
    return (
        db.query(Transaction)
        .order_by(
            Transaction.transaction_date.desc(),
            Transaction.id.desc(),
        )
        .all()
    )


def get_by_id(
    db: Session,
    transaction_id: int,
):
    return (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id
        )
        .first()
    )


def get_by_investment_id(
    db: Session,
    investment_id: int,
):
    return (
        db.query(Transaction)
        .filter(
            Transaction.investment_id
            == investment_id
        )
        .order_by(
            Transaction.transaction_date.asc(),
            Transaction.id.asc(),
        )
        .all()
    )


def get_by_broker_transaction_id(
    db: Session,
    broker_transaction_id: str,
):
    return (
        db.query(Transaction)
        .filter(
            Transaction.broker_transaction_id
            == broker_transaction_id
        )
        .first()
    )


def exists_by_broker_transaction_id(
    db: Session,
    broker_transaction_id: str,
) -> bool:
    return (
        db.query(Transaction)
        .filter(
            Transaction.broker_transaction_id
            == broker_transaction_id
        )
        .first()
        is not None
    )


def add(
    db: Session,
    transaction: Transaction,
):
    db.add(transaction)
    db.flush()

    return transaction


def delete(
    db: Session,
    transaction: Transaction,
):
    db.delete(transaction)
    db.flush()

    return True