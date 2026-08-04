from sqlalchemy.orm import Session
from sqlalchemy import func

from models.investment import Investment


def get_dashboard(db: Session):
    total_positions = db.query(Investment).count()

    total_quantity = (
        db.query(func.sum(Investment.quantity))
        .scalar()
    ) or 0

    total_invested = (
        db.query(
            func.sum(
                Investment.quantity * Investment.purchase_price
            )
        )
        .scalar()
    ) or 0

    return {
        "total_positions": total_positions,
        "total_quantity": total_quantity,
        "total_invested": round(total_invested, 2),
    }