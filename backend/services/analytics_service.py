from collections import defaultdict

from sqlalchemy.orm import Session

from repositories import analytics_repository
from repositories import dividend_analytics_repository
from repositories import investment_repository
from services.fx_service import (
    BASE_CURRENCY,
    convert_to_base_currency,
)
from services.transaction_service import recalculate_position


def convert_dividend_to_base(
    amount: float,
    currency: str,
    fx_rate: float | None,
) -> float:
    currency = (
        currency
        .strip()
        .upper()
    )

    if currency == BASE_CURRENCY:
        return float(amount)

    if (
        fx_rate is not None
        and float(fx_rate) > 0
    ):
        return (
            float(amount)
            / float(fx_rate)
        )

    return convert_to_base_currency(
        amount=float(amount),
        currency=currency,
    )


def get_allocation(
    db: Session,
):
    broker_data = (
        analytics_repository
        .get_value_by_broker(
            db
        )
    )

    asset_type_data = (
        analytics_repository
        .get_value_by_asset_type(
            db
        )
    )

    total_value = (
        analytics_repository
        .get_total_value(
            db
        )
    )

    by_broker = []

    for broker, value in broker_data:
        percentage = (
            (value / total_value) * 100
            if total_value > 0
            else 0
        )

        by_broker.append(
            {
                "broker": broker,
                "value": round(
                    value,
                    2,
                ),
                "percentage": round(
                    percentage,
                    2,
                ),
                "currency": BASE_CURRENCY,
            }
        )

    by_asset_type = []

    for asset_type, value in asset_type_data:
        percentage = (
            (value / total_value) * 100
            if total_value > 0
            else 0
        )

        by_asset_type.append(
            {
                "asset_type": asset_type,
                "value": round(
                    value,
                    2,
                ),
                "percentage": round(
                    percentage,
                    2,
                ),
                "currency": BASE_CURRENCY,
            }
        )

    return {
        "portfolio_value": round(
            total_value,
            2,
        ),
        "base_currency": BASE_CURRENCY,
        "by_broker": by_broker,
        "by_asset_type": by_asset_type,
    }


def get_performance(
    db: Session,
):
    investments = (
        investment_repository.get_all(
            db
        )
    )

    performance = []

    for investment in investments:
        invested = (
            investment.quantity
            * investment.purchase_price
        )

        current_value = (
            investment.quantity
            * investment.current_price
        )

        unrealized_profit = (
            current_value
            - invested
        )

        if invested > 0:
            unrealized_profit_percent = (
                unrealized_profit
                / invested
            ) * 100
        else:
            unrealized_profit_percent = 0

        base_invested = (
            convert_to_base_currency(
                amount=invested,
                currency=investment.currency,
            )
        )

        base_current_value = (
            convert_to_base_currency(
                amount=current_value,
                currency=investment.currency,
            )
        )

        base_unrealized_profit = (
            base_current_value
            - base_invested
        )

        performance.append(
            {
                "id": investment.id,
                "broker": investment.broker,
                "asset": investment.asset,
                "ticker": investment.ticker,
                "asset_type": (
                    investment.asset_type
                ),
                "quantity": (
                    investment.quantity
                ),
                "purchase_price": round(
                    investment.purchase_price,
                    8,
                ),
                "current_price": round(
                    investment.current_price,
                    8,
                ),
                "invested": round(
                    invested,
                    2,
                ),
                "current_value": round(
                    current_value,
                    2,
                ),
                "profit_loss": round(
                    unrealized_profit,
                    2,
                ),
                "profit_loss_percent": round(
                    unrealized_profit_percent,
                    2,
                ),
                "unrealized_profit": round(
                    unrealized_profit,
                    2,
                ),
                "unrealized_profit_percent": round(
                    unrealized_profit_percent,
                    2,
                ),
                "currency": (
                    investment.currency
                ),
                "base_invested": round(
                    base_invested,
                    2,
                ),
                "base_current_value": round(
                    base_current_value,
                    2,
                ),
                "base_profit_loss": round(
                    base_unrealized_profit,
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    return performance


def get_summary(
    db: Session,
):
    total_positions = (
        analytics_repository
        .get_total_positions(
            db
        )
    )

    total_invested = (
        analytics_repository
        .get_total_invested(
            db
        )
    )

    portfolio_value = (
        analytics_repository
        .get_total_value(
            db
        )
    )

    realized_profit = (
        analytics_repository
        .get_total_realized_profit(
            db
        )
    )

    dividends = (
        dividend_analytics_repository
        .get_all(
            db
        )
    )

    dividend_net = 0.0

    for dividend in dividends:
        dividend_net += (
            convert_dividend_to_base(
                amount=dividend.net_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

    investments = (
        analytics_repository
        .get_all_investments(
            db
        )
    )

    unrealized_profit = (
        portfolio_value
        - total_invested
    )

    total_profit = (
        unrealized_profit
        + realized_profit
        + dividend_net
    )

    if total_invested > 0:
        unrealized_profit_percent = (
            unrealized_profit
            / total_invested
        ) * 100

        total_return_percent = (
            total_profit
            / total_invested
        ) * 100
    else:
        unrealized_profit_percent = 0
        total_return_percent = 0

    best_position = None
    worst_position = None

    best_profit = None
    worst_profit = None

    for investment in investments:
        local_profit = (
            investment.quantity
            * (
                investment.current_price
                - investment.purchase_price
            )
        )

        base_profit = (
            convert_to_base_currency(
                amount=local_profit,
                currency=investment.currency,
            )
        )

        if (
            best_profit is None
            or base_profit > best_profit
        ):
            best_profit = base_profit
            best_position = (
                investment.ticker
            )

        if (
            worst_profit is None
            or base_profit < worst_profit
        ):
            worst_profit = base_profit
            worst_position = (
                investment.ticker
            )

    return {
        "positions": total_positions,
        "portfolio_value": round(
            portfolio_value,
            2,
        ),
        "total_invested": round(
            total_invested,
            2,
        ),
        "profit_loss": round(
            unrealized_profit,
            2,
        ),
        "profit_loss_percent": round(
            unrealized_profit_percent,
            2,
        ),
        "unrealized_profit": round(
            unrealized_profit,
            2,
        ),
        "unrealized_profit_percent": round(
            unrealized_profit_percent,
            2,
        ),
        "realized_profit": round(
            realized_profit,
            2,
        ),
        "dividend_net": round(
            dividend_net,
            2,
        ),
        "total_profit": round(
            total_profit,
            2,
        ),
        "total_return_percent": round(
            total_return_percent,
            2,
        ),
        "best_position": (
            best_position
        ),
        "worst_position": (
            worst_position
        ),
        "base_currency": (
            BASE_CURRENCY
        ),
    }


def get_dividend_summary(
    db: Session,
):
    dividends = (
        dividend_analytics_repository
        .get_all(
            db
        )
    )

    total_gross = 0.0
    total_tax = 0.0
    total_net = 0.0

    for dividend in dividends:
        total_gross += (
            convert_dividend_to_base(
                amount=dividend.gross_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        total_tax += (
            convert_dividend_to_base(
                amount=dividend.tax_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        total_net += (
            convert_dividend_to_base(
                amount=dividend.net_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

    payments_count = (
        len(dividends)
    )

    if total_gross > 0:
        effective_tax_rate = (
            total_tax
            / total_gross
        ) * 100
    else:
        effective_tax_rate = 0

    return {
        "total_gross": round(
            total_gross,
            2,
        ),
        "total_tax": round(
            total_tax,
            2,
        ),
        "total_net": round(
            total_net,
            2,
        ),
        "payments_count": (
            payments_count
        ),
        "effective_tax_rate": round(
            effective_tax_rate,
            2,
        ),
        "base_currency": (
            BASE_CURRENCY
        ),
    }


def get_dividends_by_year(
    db: Session,
):
    dividends = (
        dividend_analytics_repository
        .get_all(
            db
        )
    )

    yearly_data = defaultdict(
        lambda: {
            "gross_amount": 0.0,
            "tax_amount": 0.0,
            "net_amount": 0.0,
            "payments_count": 0,
        }
    )

    for dividend in dividends:
        year = (
            dividend.payment_date.year
        )

        yearly_data[
            year
        ][
            "gross_amount"
        ] += (
            convert_dividend_to_base(
                amount=dividend.gross_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        yearly_data[
            year
        ][
            "tax_amount"
        ] += (
            convert_dividend_to_base(
                amount=dividend.tax_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        yearly_data[
            year
        ][
            "net_amount"
        ] += (
            convert_dividend_to_base(
                amount=dividend.net_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        yearly_data[
            year
        ][
            "payments_count"
        ] += 1

    result = []

    for year in sorted(
        yearly_data.keys(),
        reverse=True,
    ):
        data = (
            yearly_data[year]
        )

        result.append(
            {
                "year": year,
                "gross_amount": round(
                    data[
                        "gross_amount"
                    ],
                    2,
                ),
                "tax_amount": round(
                    data[
                        "tax_amount"
                    ],
                    2,
                ),
                "net_amount": round(
                    data[
                        "net_amount"
                    ],
                    2,
                ),
                "payments_count": (
                    data[
                        "payments_count"
                    ]
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    return result


def get_dividends_by_investment(
    db: Session,
):
    dividends = (
        dividend_analytics_repository
        .get_all(
            db
        )
    )

    investments = {
        investment.id: investment
        for investment in (
            investment_repository
            .get_all(
                db
            )
        )
    }

    investment_data = defaultdict(
        lambda: {
            "gross_amount": 0.0,
            "tax_amount": 0.0,
            "net_amount": 0.0,
            "payments_count": 0,
        }
    )

    for dividend in dividends:
        investment = (
            investments.get(
                dividend.investment_id
            )
        )

        if investment is None:
            continue

        data = (
            investment_data[
                dividend.investment_id
            ]
        )

        data[
            "gross_amount"
        ] += (
            convert_dividend_to_base(
                amount=dividend.gross_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        data[
            "tax_amount"
        ] += (
            convert_dividend_to_base(
                amount=dividend.tax_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        data[
            "net_amount"
        ] += (
            convert_dividend_to_base(
                amount=dividend.net_amount,
                currency=dividend.currency,
                fx_rate=dividend.fx_rate,
            )
        )

        data[
            "payments_count"
        ] += 1

    result = []

    for (
        investment_id,
        data,
    ) in investment_data.items():
        investment = (
            investments.get(
                investment_id
            )
        )

        if investment is None:
            continue

        local_invested = (
            investment.quantity
            * investment.purchase_price
        )

        base_invested = (
            convert_to_base_currency(
                amount=local_invested,
                currency=investment.currency,
            )
        )

        if base_invested > 0:
            yield_on_cost = (
                data[
                    "net_amount"
                ]
                / base_invested
            ) * 100
        else:
            yield_on_cost = 0

        result.append(
            {
                "investment_id": (
                    investment.id
                ),
                "ticker": (
                    investment.ticker
                ),
                "asset": (
                    investment.asset
                ),
                "gross_amount": round(
                    data[
                        "gross_amount"
                    ],
                    2,
                ),
                "tax_amount": round(
                    data[
                        "tax_amount"
                    ],
                    2,
                ),
                "net_amount": round(
                    data[
                        "net_amount"
                    ],
                    2,
                ),
                "payments_count": (
                    data[
                        "payments_count"
                    ]
                ),
                "yield_on_cost": round(
                    yield_on_cost,
                    2,
                ),
                "base_currency": (
                    BASE_CURRENCY
                ),
            }
        )

    return result


def recalculate_portfolio(
    db: Session,
):
    investments = (
        investment_repository.get_all(
            db
        )
    )

    updated = 0

    try:
        for investment in investments:
            recalculate_position(
                db,
                investment.id,
            )

            updated += 1

        db.commit()

        return {
            "updated": updated,
            "positions": len(
                investments
            ),
            "message": (
                "Portfolio recalculated "
                "successfully."
            ),
        }

    except Exception:
        db.rollback()
        raise