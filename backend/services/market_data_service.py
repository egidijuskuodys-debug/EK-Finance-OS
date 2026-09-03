from datetime import date, timedelta

import yfinance as yf
from sqlalchemy import func
from sqlalchemy.orm import Session

from models.investment import Investment
from models.price_history import PriceHistory
from models.transaction import Transaction


def get_current_price(
    ticker: str,
):
    try:
        stock = yf.Ticker(ticker)

        history = stock.history(
            period="1d"
        )

        if history.empty:
            return None

        return round(
            float(
                history[
                    "Close"
                ].iloc[-1]
            ),
            2,
        )

    except Exception:
        return None


def get_historical_prices(
    ticker: str,
    start_date: date,
    end_date: date | None = None,
):
    try:
        download_end_date = end_date

        if download_end_date is None:
            download_end_date = (
                date.today()
                + timedelta(days=1)
            )

        history = yf.download(
            ticker,
            start=start_date,
            end=download_end_date,
            auto_adjust=False,
            progress=False,
        )

        if history.empty:
            return []

        prices = []

        for (
            timestamp,
            row,
        ) in history.iterrows():
            close_price = row["Close"]

            if hasattr(
                close_price,
                "iloc",
            ):
                close_price = (
                    close_price.iloc[0]
                )

            if close_price is None:
                continue

            close_price = float(
                close_price
            )

            if (
                close_price
                != close_price
            ):
                continue

            prices.append(
                {
                    "price_date": (
                        timestamp.date()
                    ),
                    "close_price": (
                        close_price
                    ),
                }
            )

        return prices

    except Exception:
        return []


def get_investment_history_start_date(
    db: Session,
    investment: Investment,
):
    first_transaction_date = (
        db.query(
            func.min(
                Transaction.transaction_date
            )
        )
        .filter(
            Transaction.investment_id
            == investment.id
        )
        .scalar()
    )

    if first_transaction_date is not None:
        return first_transaction_date

    return investment.purchase_date


def update_investment_price(
    db: Session,
    investment: Investment,
):
    price = get_current_price(
        investment.market_ticker,
    )

    if price is None:
        return False

    investment.current_price = price

    db.commit()
    db.refresh(investment)

    return True


def update_all_prices(
    db: Session,
):
    investments = db.query(
        Investment
    ).all()

    updated = 0
    failed = 0

    for investment in investments:
        success = (
            update_investment_price(
                db,
                investment,
            )
        )

        if success:
            updated += 1
        else:
            failed += 1

    return {
        "updated": updated,
        "failed": failed,
        "total": len(
            investments
        ),
    }


def update_investment_price_history(
    db: Session,
    investment: Investment,
    start_date: date | None = None,
    end_date: date | None = None,
):
    if start_date is None:
        start_date = (
            get_investment_history_start_date(
                db,
                investment,
            )
        )

    if start_date is None:
        return {
            "investment_id": (
                investment.id
            ),
            "ticker": investment.ticker,
            "market_ticker": (
                investment.market_ticker
            ),
            "inserted": 0,
            "skipped": 0,
            "received": 0,
            "status": (
                "missing_start_date"
            ),
        }

    prices = get_historical_prices(
        ticker=investment.market_ticker,
        start_date=start_date,
        end_date=end_date,
    )

    inserted = 0
    skipped = 0

    for price in prices:
        existing = (
            db.query(
                PriceHistory
            )
            .filter(
                PriceHistory.investment_id
                == investment.id,
                PriceHistory.price_date
                == price[
                    "price_date"
                ],
            )
            .first()
        )

        if existing is not None:
            skipped += 1
            continue

        price_history = PriceHistory(
            investment_id=(
                investment.id
            ),
            market_ticker=(
                investment.market_ticker
            ),
            price_date=price[
                "price_date"
            ],
            close_price=price[
                "close_price"
            ],
            currency=(
                investment.currency
            ),
        )

        db.add(
            price_history
        )

        inserted += 1

    db.commit()

    return {
        "investment_id": (
            investment.id
        ),
        "ticker": investment.ticker,
        "market_ticker": (
            investment.market_ticker
        ),
        "start_date": start_date,
        "inserted": inserted,
        "skipped": skipped,
        "received": len(prices),
    }


def update_all_price_history(
    db: Session,
):
    investments = (
        db.query(
            Investment
        )
        .all()
    )

    inserted = 0
    skipped = 0
    failed = 0

    results = []

    for investment in investments:
        result = (
            update_investment_price_history(
                db=db,
                investment=investment,
            )
        )

        inserted += result[
            "inserted"
        ]

        skipped += result[
            "skipped"
        ]

        if (
            result["received"]
            == 0
        ):
            failed += 1

        results.append(
            result
        )

    return {
        "investments": len(
            investments
        ),
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
        "results": results,
    }