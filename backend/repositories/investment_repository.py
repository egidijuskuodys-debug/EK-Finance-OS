from sqlalchemy.orm import Session

from models.investment import Investment


def get_all(
    db: Session,
):
    return db.query(Investment).all()


def get_by_id(
    db: Session,
    investment_id: int,
):
    return (
        db.query(Investment)
        .filter(
            Investment.id == investment_id
        )
        .first()
    )


def get_by_ticker(
    db: Session,
    ticker: str,
):
    return (
        db.query(Investment)
        .filter(
            Investment.ticker == ticker
        )
        .first()
    )


def get_by_ticker_and_broker(
    db: Session,
    ticker: str,
    broker: str,
):
    return (
        db.query(Investment)
        .filter(
            Investment.ticker == ticker,
            Investment.broker == broker,
        )
        .first()
    )


def exists_by_ticker(
    db: Session,
    ticker: str,
):
    return (
        db.query(Investment)
        .filter(
            Investment.ticker == ticker
        )
        .first()
        is not None
    )


def exists_by_ticker_and_broker(
    db: Session,
    ticker: str,
    broker: str,
):
    return (
        db.query(Investment)
        .filter(
            Investment.ticker == ticker,
            Investment.broker == broker,
        )
        .first()
        is not None
    )


def add(
    db: Session,
    investment: Investment,
):
    db.add(investment)
    db.flush()

    return investment


def create(
    db: Session,
    investment: Investment,
):
    db.add(investment)
    db.commit()
    db.refresh(investment)

    return investment


def update_fields(
    db: Session,
    investment: Investment,
    data: dict,
):
    for key, value in data.items():
        setattr(
            investment,
            key,
            value,
        )

    db.commit()
    db.refresh(investment)

    return investment


def delete(
    db: Session,
    investment: Investment,
):
    db.delete(investment)
    db.commit()

    return True