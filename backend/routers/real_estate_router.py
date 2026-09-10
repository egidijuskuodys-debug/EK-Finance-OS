from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.real_estate import (
    RealEstateCreate,
    RealEstateResponse,
    RealEstateSummary,
    RealEstateUpdate,
)
from schemas.real_estate_projection import (
    RealEstateProjectionResponse,
)
from services import (
    real_estate_projection_service,
    real_estate_service,
)


router = APIRouter(
    prefix="/real-estate",
    tags=["Real Estate"],
)


@router.get(
    "/",
    response_model=list[
        RealEstateResponse
    ],
)
def get_properties(
    db: Session = Depends(
        get_db
    ),
):
    return (
        real_estate_service
        .get_all_properties(
            db
        )
    )


@router.get(
    "/summary",
    response_model=RealEstateSummary,
)
def get_summary(
    db: Session = Depends(
        get_db
    ),
):
    return (
        real_estate_service
        .get_real_estate_summary(
            db
        )
    )


@router.get(
    "/{property_id}/projection",
    response_model=(
        RealEstateProjectionResponse
    ),
)
def get_property_projection(
    property_id: int,
    annual_property_growth: float = Query(
        default=2.0,
        gt=-100,
        le=100,
    ),
    projection_years: int = Query(
        default=20,
        ge=1,
        le=40,
    ),
    db: Session = Depends(
        get_db
    ),
):
    projection = (
        real_estate_projection_service
        .get_real_estate_projection(
            db=db,
            property_id=property_id,
            annual_property_growth=(
                annual_property_growth
            ),
            projection_years=(
                projection_years
            ),
        )
    )

    if projection is None:
        raise HTTPException(
            status_code=(
                status
                .HTTP_404_NOT_FOUND
            ),
            detail=(
                "Real estate property "
                "not found."
            ),
        )

    return projection


@router.get(
    "/{property_id}",
    response_model=RealEstateResponse,
)
def get_property(
    property_id: int,
    db: Session = Depends(
        get_db
    ),
):
    property_data = (
        real_estate_service
        .get_property_by_id(
            db,
            property_id,
        )
    )

    if property_data is None:
        raise HTTPException(
            status_code=(
                status
                .HTTP_404_NOT_FOUND
            ),
            detail=(
                "Real estate property "
                "not found."
            ),
        )

    return property_data


@router.post(
    "/",
    response_model=RealEstateResponse,
    status_code=(
        status.HTTP_201_CREATED
    ),
)
def create_property(
    property_data: RealEstateCreate,
    db: Session = Depends(
        get_db
    ),
):
    return (
        real_estate_service
        .create_property(
            db,
            property_data,
        )
    )


@router.put(
    "/{property_id}",
    response_model=RealEstateResponse,
)
def update_property(
    property_id: int,
    property_data: RealEstateUpdate,
    db: Session = Depends(
        get_db
    ),
):
    updated_property = (
        real_estate_service
        .update_property(
            db,
            property_id,
            property_data,
        )
    )

    if updated_property is None:
        raise HTTPException(
            status_code=(
                status
                .HTTP_404_NOT_FOUND
            ),
            detail=(
                "Real estate property "
                "not found."
            ),
        )

    return updated_property


@router.delete(
    "/{property_id}",
)
def delete_property(
    property_id: int,
    db: Session = Depends(
        get_db
    ),
):
    deleted = (
        real_estate_service
        .delete_property(
            db,
            property_id,
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=(
                status
                .HTTP_404_NOT_FOUND
            ),
            detail=(
                "Real estate property "
                "not found."
            ),
        )

    return {
        "message": (
            "Real estate property "
            "deleted successfully."
        )
    }