from hashlib import sha256
from typing import Any

from sqlalchemy.orm import Session

from models.cash_movement import CashMovement
from repositories import cash_movement_repository


def build_broker_movement_id(
    movement_data: dict[str, Any],
) -> str:
    broker = (
        movement_data["broker"]
        .strip()
        .upper()
    )

    raw = "|".join(
        [
            broker,
            movement_data["movement_type"],
            str(
                movement_data["movement_date"]
            ),
            str(
                movement_data["amount"]
            ),
            movement_data["currency"],
            movement_data.get(
                "description",
                "",
            ),
        ]
    )

    return sha256(
        raw.encode("utf-8")
    ).hexdigest()


def import_cash_movements(
    db: Session,
    cash_movements: list[
        dict[str, Any]
    ],
) -> dict[str, int]:
    imported = 0
    skipped = 0

    for movement_data in cash_movements:
        broker_movement_id = (
            build_broker_movement_id(
                movement_data
            )
        )

        duplicate_exists = (
            cash_movement_repository
            .exists_by_broker_movement_id(
                db,
                broker_movement_id,
            )
        )

        if duplicate_exists:
            skipped += 1
            continue

        fx_rate = movement_data.get(
            "fx_rate"
        )

        if fx_rate is not None:
            fx_rate = float(fx_rate)

            if fx_rate <= 0:
                fx_rate = None

        cash_movement = CashMovement(
            broker=movement_data["broker"],
            movement_type=(
                movement_data[
                    "movement_type"
                ]
            ),
            amount=movement_data[
                "amount"
            ],
            currency=movement_data[
                "currency"
            ],
            fx_rate=fx_rate,
            movement_date=(
                movement_data[
                    "movement_date"
                ]
            ),
            description=(
                movement_data.get(
                    "description"
                )
            ),
            broker_movement_id=(
                broker_movement_id
            ),
        )

        cash_movement_repository.add(
            db,
            cash_movement,
        )

        imported += 1

    return {
        "imported": imported,
        "skipped": skipped,
    }