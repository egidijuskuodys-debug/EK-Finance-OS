from sqlalchemy.orm import Session

from models.cash_movement import CashMovement


def get_all(
    db: Session,
):
    return (
        db.query(CashMovement)
        .order_by(
            CashMovement.movement_date.desc(),
            CashMovement.id.desc(),
        )
        .all()
    )


def get_by_id(
    db: Session,
    movement_id: int,
):
    return (
        db.query(CashMovement)
        .filter(
            CashMovement.id == movement_id
        )
        .first()
    )


def get_by_broker_movement_id(
    db: Session,
    broker_movement_id: str,
):
    return (
        db.query(CashMovement)
        .filter(
            CashMovement.broker_movement_id
            == broker_movement_id
        )
        .first()
    )


def exists_by_broker_movement_id(
    db: Session,
    broker_movement_id: str,
) -> bool:
    return (
        db.query(CashMovement)
        .filter(
            CashMovement.broker_movement_id
            == broker_movement_id
        )
        .first()
        is not None
    )


def add(
    db: Session,
    cash_movement: CashMovement,
):
    db.add(cash_movement)
    db.flush()

    return cash_movement


def delete(
    db: Session,
    cash_movement: CashMovement,
):
    db.delete(cash_movement)
    db.flush()

    return True