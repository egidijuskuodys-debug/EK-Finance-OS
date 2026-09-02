from functools import lru_cache

import yfinance as yf


BASE_CURRENCY = "EUR"


def _get_history_rate(
    ticker: str,
) -> float | None:
    try:
        fx = yf.Ticker(ticker)

        history = fx.history(
            period="5d",
        )

        if history.empty:
            return None

        close_values = (
            history["Close"]
            .dropna()
        )

        if close_values.empty:
            return None

        rate = float(
            close_values.iloc[-1]
        )

        if rate <= 0:
            return None

        return rate

    except Exception:
        return None


def _get_fast_info_rate(
    ticker: str,
) -> float | None:
    try:
        fx = yf.Ticker(ticker)

        fast_info = fx.fast_info

        rate = fast_info.get(
            "last_price"
        )

        if rate is None:
            return None

        rate = float(rate)

        if rate <= 0:
            return None

        return rate

    except Exception:
        return None


def _retrieve_direct_rate(
    from_currency: str,
    to_currency: str,
) -> float | None:
    ticker = (
        f"{from_currency}"
        f"{to_currency}=X"
    )

    rate = _get_history_rate(
        ticker
    )

    if rate is not None:
        return rate

    return _get_fast_info_rate(
        ticker
    )


@lru_cache(maxsize=32)
def get_fx_rate(
    from_currency: str,
    to_currency: str = BASE_CURRENCY,
) -> float:
    from_currency = (
        from_currency
        .strip()
        .upper()
    )

    to_currency = (
        to_currency
        .strip()
        .upper()
    )

    if not from_currency:
        raise ValueError(
            "Source currency is required."
        )

    if not to_currency:
        raise ValueError(
            "Target currency is required."
        )

    if from_currency == to_currency:
        return 1.0

    direct_rate = (
        _retrieve_direct_rate(
            from_currency,
            to_currency,
        )
    )

    if direct_rate is not None:
        return direct_rate

    reverse_rate = (
        _retrieve_direct_rate(
            to_currency,
            from_currency,
        )
    )

    if (
        reverse_rate is not None
        and reverse_rate > 0
    ):
        return 1.0 / reverse_rate

    raise ValueError(
        f"Could not retrieve FX rate for "
        f"{from_currency}/"
        f"{to_currency}."
    )


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str = BASE_CURRENCY,
) -> float:
    rate = get_fx_rate(
        from_currency=from_currency,
        to_currency=to_currency,
    )

    return amount * rate


def convert_to_base_currency(
    amount: float,
    currency: str,
) -> float:
    return convert_currency(
        amount=amount,
        from_currency=currency,
        to_currency=BASE_CURRENCY,
    )


def clear_fx_cache() -> None:
    get_fx_rate.cache_clear()