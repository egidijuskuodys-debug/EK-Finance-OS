from sqlalchemy.orm import Session

from models.portfolio_target import PortfolioTarget


def get_all(db: Session):
    return (
        db.query(PortfolioTarget)
        .order_by(
            PortfolioTarget.dimension.asc(),
            PortfolioTarget.target_key.asc(),
        )
        .all()
    )


def get_by_id(db: Session, target_id: int):
    return (
        db.query(PortfolioTarget)
        .filter(PortfolioTarget.id == target_id)
        .first()
    )


def get_by_dimension_and_key(
    db: Session,
    dimension: str,
    target_key: str,
):
    return (
        db.query(PortfolioTarget)
        .filter(
            PortfolioTarget.dimension == dimension,
            PortfolioTarget.target_key == target_key,
        )
        .first()
    )


def create(db: Session, target: PortfolioTarget):
    db.add(target)
    db.commit()
    db.refresh(target)
    return target


def update_fields(
    db: Session,
    target: PortfolioTarget,
    data: dict,
):
    for key, value in data.items():
        setattr(target, key, value)

    db.commit()
    db.refresh(target)
    return target


def delete(db: Session, target: PortfolioTarget):
    db.delete(target)
    db.commit()
