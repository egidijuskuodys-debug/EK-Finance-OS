from sqlalchemy.orm import Session

from models.transaction_lot import TransactionLot


def get_all(db: Session):
    return (
        db.query(TransactionLot)
        .order_by(
            TransactionLot.purchase_date.asc(),
            TransactionLot.id.asc(),
        )
        .all()
    )


def get_by_investment(
    db: Session,
    investment_id: int,
):
    return (
        db.query(TransactionLot)
        .filter(
            TransactionLot.investment_id == investment_id,
            TransactionLot.remaining_quantity > 0,
        )
        .order_by(
            TransactionLot.purchase_date.asc(),
            TransactionLot.id.asc(),
        )
        .all()
    )


def get_by_buy_transaction(
    db: Session,
    transaction_id: int,
):
    return (
        db.query(TransactionLot)
        .filter(
            TransactionLot.buy_transaction_id == transaction_id
        )
        .first()
    )


def create(
    db: Session,
    lot: TransactionLot,
):
    db.add(lot)
    db.flush()

    return lot


def delete(
    db: Session,
    lot: TransactionLot,
):
    db.delete(lot)
    db.flush()


def update(
    db: Session,
    lot: TransactionLot,
):
    db.flush()

    return lot