from sqlalchemy.orm import Session

from models.portfolio_target import PortfolioTarget
from repositories import portfolio_target_repository
from schemas.portfolio_target_schema import (
    PortfolioTargetCreate,
    PortfolioTargetUpdate,
)


def get_portfolio_targets(db: Session):
    return portfolio_target_repository.get_all(db)


def get_portfolio_target_by_id(
    db: Session,
    target_id: int,
):
    return portfolio_target_repository.get_by_id(
        db,
        target_id,
    )


def create_portfolio_target(
    db: Session,
    target_data: PortfolioTargetCreate,
):
    dimension = target_data.dimension.strip()
    target_key = target_data.target_key.strip()

    existing = (
        portfolio_target_repository.get_by_dimension_and_key(
            db,
            dimension,
            target_key,
        )
    )

    if existing is not None:
        raise ValueError(
            "Portfolio target already exists."
        )

    target = PortfolioTarget(
        dimension=dimension,
        target_key=target_key,
        target_percentage=target_data.target_percentage,
    )

    return portfolio_target_repository.create(
        db,
        target,
    )


def update_portfolio_target(
    db: Session,
    target_id: int,
    target_data: PortfolioTargetUpdate,
):
    target = portfolio_target_repository.get_by_id(
        db,
        target_id,
    )

    if target is None:
        return None

    update_data = target_data.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )

    if "dimension" in update_data:
        update_data["dimension"] = (
            update_data["dimension"].strip()
        )

    if "target_key" in update_data:
        update_data["target_key"] = (
            update_data["target_key"].strip()
        )

    dimension = update_data.get(
        "dimension",
        target.dimension,
    )
    target_key = update_data.get(
        "target_key",
        target.target_key,
    )

    existing = (
        portfolio_target_repository.get_by_dimension_and_key(
            db,
            dimension,
            target_key,
        )
    )

    if existing is not None and existing.id != target.id:
        raise ValueError(
            "Portfolio target already exists."
        )

    return portfolio_target_repository.update_fields(
        db,
        target,
        update_data,
    )


def delete_portfolio_target(
    db: Session,
    target_id: int,
):
    target = portfolio_target_repository.get_by_id(
        db,
        target_id,
    )

    if target is None:
        return None

    portfolio_target_repository.delete(
        db,
        target,
    )

    return {
        "message": "Portfolio target deleted successfully"
    }
