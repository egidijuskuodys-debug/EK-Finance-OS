from typing import Optional


ETF_TICKERS = {
    "VWCE",
    "VHYL",
    "NUCL",
    "DFNS",
}


STOCK_TICKERS = {
    "AAL",
    "AMZN",
}


def classify_asset_type(
    ticker: str,
    broker_asset_category: Optional[str] = None,
) -> str:
    normalized_ticker = (
        ticker
        .strip()
        .upper()
    )

    normalized_category = (
        broker_asset_category
        .strip()
        .upper()
        if broker_asset_category
        else ""
    )

    if normalized_ticker in ETF_TICKERS:
        return "ETF"

    if normalized_ticker in STOCK_TICKERS:
        return "Stock"

    if normalized_category in {
        "ETF",
        "ETFS",
        "FUND",
        "FUNDS",
    }:
        return "ETF"

    if normalized_category in {
        "STOCK",
        "STOCKS",
        "EQUITY",
        "EQUITIES",
    }:
        return "Stock"

    return "Other"