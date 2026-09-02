import yfinance as yf
from sqlalchemy.orm import Session

from models.investment import Investment


def get_current_price(ticker: str):
    try:
        stock = yf.Ticker(ticker)

        history = stock.history(period="1d")

        if history.empty:
            return None

        return round(
            float(history["Close"].iloc[-1]),
            2,
        )

    except Exception:
        return None


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

        success = update_investment_price(
            db,
            investment,
        )

        if success:
            updated += 1
        else:
            failed += 1

    return {
        "updated": updated,
        "failed": failed,
        "total": len(investments),
    }