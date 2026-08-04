from sqlalchemy.orm import Session

from models.investment import Investment
from schemas.investment import InvestmentCreate


def create_investment(db: Session, investment: InvestmentCreate):
    db_investment = Investment(
        broker=investment.broker,
        asset=investment.asset,
        ticker=investment.ticker,
        quantity=investment.quantity,
        purchase_price=investment.purchase_price,
        currency=investment.currency,
        purchase_date=investment.purchase_date,
    )

    db.add(db_investment)
    db.commit()
    db.refresh(db_investment)

    return db_investment


def get_investments(db: Session):
    return db.query(Investment).all()


def delete_investment(db: Session, investment_id: int):
    investment = (
        db.query(Investment)
        .filter(Investment.id == investment_id)
        .first()
    )

    if investment is None:
        return None

    db.delete(investment)
    db.commit()

    return {"message": "Investment deleted successfully"}