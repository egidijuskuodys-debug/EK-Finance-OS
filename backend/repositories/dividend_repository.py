from sqlalchemy.orm import Session

from models.dividend import Dividend


def get_all(
    db: Session,
):
    return (
        db.query(Dividend)
        .order_by(
            Dividend.payment_date.desc(),
            Dividend.id.desc(),
        )
        .all()
    )


def get_by_id(
    db: Session,
    dividend_id: int,
):
    return (
        db.query(Dividend)
        .filter(
            Dividend.id == dividend_id
        )
        .first()
    )


def get_by_investment_id(
    db: Session,
    investment_id: int,
):
    return (
        db.query(Dividend)
        .filter(
            Dividend.investment_id == investment_id
        )
        .order_by(
            Dividend.payment_date.desc(),
            Dividend.id.desc(),
        )
        .all()
    )


def exists(
    db: Session,
    investment_id: int,
    payment_date,
    net_amount: float,
):
    return (
        db.query(Dividend)
        .filter(
            Dividend.investment_id == investment_id,
            Dividend.payment_date == payment_date,
            Dividend.net_amount == net_amount,
        )
        .first()
        is not None
    )


def add(
    db: Session,
    dividend: Dividend,
):
    db.add(dividend)
    db.flush()

    return dividend


def create(
    db: Session,
    dividend: Dividend,
):
    db.add(dividend)
    db.commit()
    db.refresh(dividend)

    return dividend


def update_fields(
    db: Session,
    dividend: Dividend,
    data: dict,
):
    for key, value in data.items():
        setattr(
            dividend,
            key,
            value,
        )

    db.commit()
    db.refresh(dividend)

    return dividend


def delete(
    db: Session,
    dividend: Dividend,
):
    db.delete(dividend)
    db.commit()

    return True