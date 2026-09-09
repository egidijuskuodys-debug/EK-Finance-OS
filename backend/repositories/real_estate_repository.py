from sqlalchemy.orm import Session

from models.real_estate import (
    RealEstateProperty,
)
from schemas.real_estate import (
    RealEstateCreate,
    RealEstateUpdate,
)


def get_all_properties(
    db: Session,
):
    return (
        db.query(
            RealEstateProperty
        )
        .order_by(
            RealEstateProperty.id
        )
        .all()
    )


def get_property_by_id(
    db: Session,
    property_id: int,
):
    return (
        db.query(
            RealEstateProperty
        )
        .filter(
            RealEstateProperty.id
            == property_id
        )
        .first()
    )


def create_property(
    db: Session,
    property_data: RealEstateCreate,
):
    data = property_data.model_dump()

    data["currency"] = (
        data["currency"]
        .strip()
        .upper()
    )

    property_record = (
        RealEstateProperty(
            **data
        )
    )

    db.add(
        property_record
    )

    db.commit()

    db.refresh(
        property_record
    )

    return property_record


def update_property(
    db: Session,
    property_record: RealEstateProperty,
    property_data: RealEstateUpdate,
):
    update_data = (
        property_data.model_dump(
            exclude_unset=True
        )
    )

    if (
        "currency"
        in update_data
        and update_data["currency"]
        is not None
    ):
        update_data["currency"] = (
            update_data["currency"]
            .strip()
            .upper()
        )

    for field, value in (
        update_data.items()
    ):
        setattr(
            property_record,
            field,
            value,
        )

    db.commit()

    db.refresh(
        property_record
    )

    return property_record


def delete_property(
    db: Session,
    property_record: RealEstateProperty,
):
    db.delete(
        property_record
    )

    db.commit()