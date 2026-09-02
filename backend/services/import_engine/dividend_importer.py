from hashlib import sha256
from typing import Any

from sqlalchemy.orm import Session

from models.dividend import Dividend
from repositories import (
    dividend_repository,
    investment_repository,
)


def build_broker_dividend_id(
    dividend_data: dict[str, Any],
) -> str:
    broker = (
        dividend_data["broker"]
        .strip()
        .upper()
    )

    raw = "|".join(
        [
            broker,
            dividend_data["ticker"],
            str(
                dividend_data["payment_date"]
            ),
            str(
                dividend_data["gross_amount"]
            ),
            str(
                dividend_data["tax_amount"]
            ),
            str(
                dividend_data["net_amount"]
            ),
            dividend_data["currency"],
        ]
    )

    return sha256(
        raw.encode("utf-8")
    ).hexdigest()


def import_dividends(
    db: Session,
    dividends: list[dict[str, Any]],
) -> dict[str, int]:
    imported = 0
    skipped = 0

    for dividend_data in dividends:
        investment = (
            investment_repository
            .get_by_ticker_and_broker(
                db,
                ticker=dividend_data["ticker"],
                broker=dividend_data["broker"],
            )
        )

        if investment is None:
            continue

        broker_dividend_id = (
            build_broker_dividend_id(
                dividend_data
            )
        )

        if (
            db.query(Dividend)
            .filter(
                Dividend.broker_dividend_id
                == broker_dividend_id
            )
            .first()
            is not None
        ):
            skipped += 1
            continue

        fx_rate = dividend_data.get(
            "fx_rate"
        )

        if fx_rate is not None:
            fx_rate = float(
                fx_rate
            )

            if fx_rate <= 0:
                raise ValueError(
                    f"Invalid dividend FX rate for "
                    f"{dividend_data['broker']} / "
                    f"{dividend_data['ticker']}: "
                    f"{fx_rate}."
                )

        dividend = Dividend(
            investment_id=investment.id,
            broker_dividend_id=(
                broker_dividend_id
            ),
            payment_date=dividend_data[
                "payment_date"
            ],
            gross_amount=dividend_data[
                "gross_amount"
            ],
            tax_amount=dividend_data[
                "tax_amount"
            ],
            net_amount=dividend_data[
                "net_amount"
            ],
            currency=dividend_data[
                "currency"
            ],
            fx_rate=fx_rate,
            notes=dividend_data.get(
                "description"
            ),
        )

        dividend_repository.add(
            db,
            dividend,
        )

        imported += 1

    return {
        "imported": imported,
        "skipped": skipped,
    }