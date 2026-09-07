from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.portfolio_target_schema import (
    PortfolioTargetCreate,
    PortfolioTargetResponse,
    PortfolioTargetUpdate,
)
from services.portfolio_target_service import (
    create_portfolio_target,
    delete_portfolio_target,
    get_portfolio_target_by_id,
    get_portfolio_targets,
    update_portfolio_target,
)


router = APIRouter(
    prefix="/portfolio-targets",
    tags=["Portfolio Targets"],
)


@router.get(
    "/",
    response_model=list[PortfolioTargetResponse],
)
def list_portfolio_targets(
    db: Session = Depends(get_db),
):
    return get_portfolio_targets(db)


@router.get(
    "/{target_id}",
    response_model=PortfolioTargetResponse,
)
def read_portfolio_target(
    target_id: int,
    db: Session = Depends(get_db),
):
    target = get_portfolio_target_by_id(
        db,
        target_id,
    )

    if target is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio target not found",
        )

    return target


@router.post(
    "/",
    response_model=PortfolioTargetResponse,
    status_code=201,
)
def add_portfolio_target(
    target: PortfolioTargetCreate,
    db: Session = Depends(get_db),
):
    try:
        return create_portfolio_target(
            db,
            target,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.put(
    "/{target_id}",
    response_model=PortfolioTargetResponse,
)
def edit_portfolio_target(
    target_id: int,
    target: PortfolioTargetUpdate,
    db: Session = Depends(get_db),
):
    try:
        result = update_portfolio_target(
            db,
            target_id,
            target,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail="Portfolio target not found",
            )

        return result
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.delete("/{target_id}")
def remove_portfolio_target(
    target_id: int,
    db: Session = Depends(get_db),
):
    result = delete_portfolio_target(
        db,
        target_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio target not found",
        )

    return result
