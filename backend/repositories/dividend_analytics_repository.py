from sqlalchemy.orm import Session

from models.dividend import Dividend


def get_all(
    db: Session,
):
    return (
        db.query(Dividend)
        .order_by(
            Dividend.payment_date.asc(),
            Dividend.id.asc(),
        )
        .all()
    )


def get_payments_count(
    db: Session,
):
    return (
        db.query(Dividend)
        .count()
    )


def get_total_gross(
    db: Session,
):
    dividends = get_all(db)

    return sum(
        dividend.gross_amount
        for dividend in dividends
    )


def get_total_tax(
    db: Session,
):
    dividends = get_all(db)

    return sum(
        dividend.tax_amount
        for dividend in dividends
    )


def get_total_net(
    db: Session,
):
    dividends = get_all(db)

    return sum(
        dividend.net_amount
        for dividend in dividends
    )