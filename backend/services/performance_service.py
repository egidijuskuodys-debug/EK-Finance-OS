from datetime import date

from sqlalchemy.orm import Session

from repositories import (
    analytics_repository,
    cash_movement_repository,
)
from services.cash_balance_service import (
    get_cash_balance,
)
from services.cash_flow_service import (
    DEPOSIT_TYPES,
    WITHDRAWAL_TYPES,
    convert_cash_movement_to_base,
    get_cash_flow_summary,
    normalize_movement_type,
)
from services.fx_service import BASE_CURRENCY


XIRR_TOLERANCE = 0.0000001
XIRR_MAX_ITERATIONS = 200


def calculate_xnpv(
    rate: float,
    cash_flows: list[
        tuple[date, float]
    ],
) -> float:
    if not cash_flows:
        return 0.0

    first_date = cash_flows[0][0]

    total = 0.0

    for (
        cash_flow_date,
        amount,
    ) in cash_flows:
        days = (
            cash_flow_date
            - first_date
        ).days

        years = (
            days / 365.0
        )

        total += (
            amount
            / (
                (1.0 + rate)
                ** years
            )
        )

    return total


def calculate_xirr(
    cash_flows: list[
        tuple[date, float]
    ],
) -> float | None:
    if len(cash_flows) < 2:
        return None

    cash_flows = sorted(
        cash_flows,
        key=lambda item: item[0],
    )

    has_negative = any(
        amount < 0
        for _, amount in cash_flows
    )

    has_positive = any(
        amount > 0
        for _, amount in cash_flows
    )

    if not (
        has_negative
        and has_positive
    ):
        return None

    lower_rate = -0.9999
    upper_rate = 10.0

    lower_value = calculate_xnpv(
        lower_rate,
        cash_flows,
    )

    upper_value = calculate_xnpv(
        upper_rate,
        cash_flows,
    )

    while (
        lower_value
        * upper_value
        > 0
        and upper_rate < 1000000
    ):
        upper_rate *= 2

        upper_value = calculate_xnpv(
            upper_rate,
            cash_flows,
        )

    if (
        lower_value
        * upper_value
        > 0
    ):
        return None

    for _ in range(
        XIRR_MAX_ITERATIONS
    ):
        middle_rate = (
            lower_rate
            + upper_rate
        ) / 2

        middle_value = calculate_xnpv(
            middle_rate,
            cash_flows,
        )

        if (
            abs(middle_value)
            < XIRR_TOLERANCE
        ):
            return middle_rate

        if (
            lower_value
            * middle_value
            <= 0
        ):
            upper_rate = middle_rate
            upper_value = middle_value
        else:
            lower_rate = middle_rate
            lower_value = middle_value

    return (
        lower_rate
        + upper_rate
    ) / 2


def get_portfolio_xirr(
    db: Session,
):
    movements = (
        cash_movement_repository
        .get_all(
            db
        )
    )

    cash_flows = []

    for movement in movements:
        movement_type = (
            normalize_movement_type(
                movement.movement_type
            )
        )

        amount_base = (
            convert_cash_movement_to_base(
                amount=movement.amount,
                currency=movement.currency,
                fx_rate=movement.fx_rate,
            )
        )

        if movement_type in DEPOSIT_TYPES:
            cash_flows.append(
                (
                    movement.movement_date,
                    -abs(amount_base),
                )
            )

        elif (
            movement_type
            in WITHDRAWAL_TYPES
        ):
            cash_flows.append(
                (
                    movement.movement_date,
                    abs(amount_base),
                )
            )

    securities_value = (
        analytics_repository
        .get_total_value(
            db
        )
    )

    cash_result = get_cash_balance(
        db
    )

    cash_balance = float(
        cash_result.get(
            "cash_balance",
            0.0,
        )
    )

    total_wealth = (
        securities_value
        + cash_balance
    )

    cash_flow_summary = (
        get_cash_flow_summary(
            db
        )
    )

    total_deposits = float(
        cash_flow_summary.get(
            "total_deposits",
            0.0,
        )
    )

    total_withdrawals = float(
        cash_flow_summary.get(
            "total_withdrawals",
            0.0,
        )
    )

    net_contributions = float(
        cash_flow_summary.get(
            "net_contributions",
            0.0,
        )
    )

    investment_gain = (
        total_wealth
        - net_contributions
    )

    if net_contributions > 0:
        investment_gain_percent = (
            investment_gain
            / net_contributions
        ) * 100
    else:
        investment_gain_percent = 0.0

    valuation_date = date.today()

    if total_wealth > 0:
        cash_flows.append(
            (
                valuation_date,
                total_wealth,
            )
        )

    xirr = calculate_xirr(
        cash_flows
    )

    return {
        "xirr": (
            round(
                xirr * 100,
                2,
            )
            if xirr is not None
            else None
        ),
        "portfolio_value": round(
            total_wealth,
            2,
        ),
        "securities_value": round(
            securities_value,
            2,
        ),
        "cash_balance": round(
            cash_balance,
            2,
        ),
        "total_wealth": round(
            total_wealth,
            2,
        ),
        "total_deposits": round(
            total_deposits,
            2,
        ),
        "total_withdrawals": round(
            total_withdrawals,
            2,
        ),
        "net_contributions": round(
            net_contributions,
            2,
        ),
        "investment_gain": round(
            investment_gain,
            2,
        ),
        "investment_gain_percent": round(
            investment_gain_percent,
            2,
        ),
        "valuation_date": (
            valuation_date
        ),
        "cash_flows_count": len(
            cash_flows
        ),
        "base_currency": (
            BASE_CURRENCY
        ),
    }