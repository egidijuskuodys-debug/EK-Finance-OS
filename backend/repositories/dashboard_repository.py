from sqlalchemy import func
from sqlalchemy.orm import Session

from models.investment import Investment


def get_total_positions(
    db: Session,
):
    return (
        db.query(Investment)
        .count()
    )


def get_total_quantity(
    db: Session,
):
    return (
        db.query(
            func.sum(
                Investment.quantity
            )
        )
        .scalar()
        or 0
    )


def get_all_investments(
    db: Session,
):
    return (
        db.query(Investment)
        .all()
    )