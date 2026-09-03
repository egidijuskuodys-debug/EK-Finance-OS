MARKET_TICKER_MAP: dict[
    tuple[str, str],
    str,
] = {
    # Revolut ETF
    ("REVOLUT", "EXI2"): "EXI2.DE",
    ("REVOLUT", "I500"): "I500.DE",

    # Interactive Brokers ETF
    (
        "INTERACTIVE BROKERS",
        "DFNS",
    ): "DFNS.L",
    (
        "INTERACTIVE BROKERS",
        "NUCL",
    ): "NUKL.DE",
    (
        "INTERACTIVE BROKERS",
        "VHYL",
    ): "VHYL.AS",
    (
        "INTERACTIVE BROKERS",
        "VWCE",
    ): "VWCE.DE",
}


def resolve_market_ticker(
    broker: str,
    ticker: str,
) -> str:
    normalized_broker = (
        broker.strip().upper()
    )

    normalized_ticker = (
        ticker.strip().upper()
    )

    key = (
        normalized_broker,
        normalized_ticker,
    )

    return MARKET_TICKER_MAP.get(
        key,
        normalized_ticker,
    )