from bisect import bisect_right
from datetime import date, timedelta
from functools import lru_cache

import yfinance as yf


BASE_CURRENCY = "EUR"

HISTORICAL_FX_START_DATE = date(
    2000,
    1,
    1,
)


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


@lru_cache(maxsize=16)
def _get_historical_fx_series(
    ticker: str,
) -> tuple[
    tuple[date, ...],
    tuple[float, ...],
]:
    try:
        history = yf.download(
            ticker,
            start=HISTORICAL_FX_START_DATE,
            end=(
                date.today()
                + timedelta(days=2)
            ),
            auto_adjust=False,
            progress=False,
        )

        if history.empty:
            return (
                tuple(),
                tuple(),
            )

        dates: list[date] = []
        rates: list[float] = []

        for (
            timestamp,
            row,
        ) in history.iterrows():
            close_value = row["Close"]

            if hasattr(
                close_value,
                "iloc",
            ):
                close_value = (
                    close_value.iloc[0]
                )

            if close_value is None:
                continue

            rate = float(
                close_value
            )

            if rate != rate:
                continue

            if rate <= 0:
                continue

            dates.append(
                timestamp.date()
            )

            rates.append(
                rate
            )

        return (
            tuple(dates),
            tuple(rates),
        )

    except Exception:
        return (
            tuple(),
            tuple(),
        )


def _find_historical_rate(
    ticker: str,
    rate_date: date,
) -> float | None:
    dates, rates = (
        _get_historical_fx_series(
            ticker
        )
    )

    if not dates:
        return None

    index = (
        bisect_right(
            dates,
            rate_date,
        )
        - 1
    )

    if index < 0:
        return None

    rate = rates[index]

    if rate <= 0:
        return None

    return rate


@lru_cache(maxsize=4096)
def get_historical_fx_rate(
    from_currency: str,
    rate_date: date,
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

    direct_ticker = (
        f"{from_currency}"
        f"{to_currency}=X"
    )

    direct_rate = (
        _find_historical_rate(
            ticker=direct_ticker,
            rate_date=rate_date,
        )
    )

    if direct_rate is not None:
        return direct_rate

    reverse_ticker = (
        f"{to_currency}"
        f"{from_currency}=X"
    )

    reverse_rate = (
        _find_historical_rate(
            ticker=reverse_ticker,
            rate_date=rate_date,
        )
    )

    if (
        reverse_rate is not None
        and reverse_rate > 0
    ):
        return 1.0 / reverse_rate

    raise ValueError(
        f"Could not retrieve historical "
        f"FX rate for "
        f"{from_currency}/"
        f"{to_currency} on "
        f"{rate_date}."
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


def convert_historical_currency(
    amount: float,
    currency: str,
    rate_date: date,
    to_currency: str = BASE_CURRENCY,
) -> float:
    rate = get_historical_fx_rate(
        from_currency=currency,
        rate_date=rate_date,
        to_currency=to_currency,
    )

    return amount * rate


def clear_fx_cache() -> None:
    get_fx_rate.cache_clear()
    get_historical_fx_rate.cache_clear()
    _get_historical_fx_series.cache_clear()