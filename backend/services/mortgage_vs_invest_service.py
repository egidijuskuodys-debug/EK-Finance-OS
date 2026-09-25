import calendar
from datetime import date

from sqlalchemy.orm import Session

from repositories import (
    real_estate_repository,
)
from schemas.mortgage_vs_invest import (
    MortgageVsInvestRequest,
)


def add_months(
    source_date: date,
    months: int,
) -> date:
    month_index = (
        source_date.month
        - 1
        + months
    )

    year = (
        source_date.year
        + month_index // 12
    )

    month = (
        month_index % 12
        + 1
    )

    last_day = calendar.monthrange(
        year,
        month,
    )[1]

    day = min(
        source_date.day,
        last_day,
    )

    return date(
        year,
        month,
        day,
    )


def get_remaining_months(
    calculation_date: date,
    loan_end_date: date | None,
) -> int:
    if loan_end_date is None:
        return 240

    months = (
        (
            loan_end_date.year
            - calculation_date.year
        )
        * 12
        + (
            loan_end_date.month
            - calculation_date.month
        )
    )

    return max(
        months,
        1,
    )


def simulate_strategy(
    *,
    loan_balance: float,
    annual_interest_rate: float,
    remaining_months: int,
    calculation_date: date,
    loan_end_date: date,
    total_monthly_budget: float,
    desired_mortgage_payment: float,
    annual_investment_return: float,
):
    balance = loan_balance
    investment_value = 0.0

    total_interest = 0.0
    payoff_months = remaining_months
    payoff_date = loan_end_date

    monthly_interest_rate = (
        annual_interest_rate
        / 100
        / 12
    )

    monthly_investment_return = (
        annual_investment_return
        / 100
        / 12
    )

    for month_number in range(
        1,
        remaining_months + 1,
    ):
        investment_value *= (
            1
            + monthly_investment_return
        )

        actual_mortgage_payment = 0.0

        if balance > 0:
            interest_amount = (
                balance
                * monthly_interest_rate
            )

            total_interest += (
                interest_amount
            )

            amount_due = (
                balance
                + interest_amount
            )

            actual_mortgage_payment = min(
                desired_mortgage_payment,
                amount_due,
            )

            principal_amount = max(
                actual_mortgage_payment
                - interest_amount,
                0.0,
            )

            principal_amount = min(
                principal_amount,
                balance,
            )

            balance -= principal_amount

            if balance <= 0.005:
                balance = 0.0

                payoff_months = (
                    month_number
                )

                payoff_date = add_months(
                    calculation_date,
                    month_number,
                )

        investment_contribution = max(
            total_monthly_budget
            - actual_mortgage_payment,
            0.0,
        )

        investment_value += (
            investment_contribution
        )

    return {
        "remaining_balance": balance,
        "payoff_months": (
            payoff_months
        ),
        "payoff_date": (
            payoff_date
        ),
        "interest_paid": (
            total_interest
        ),
        "investment_value": (
            investment_value
        ),
    }


def find_break_even_return(
    *,
    loan_balance: float,
    annual_interest_rate: float,
    remaining_months: int,
    calculation_date: date,
    loan_end_date: date,
    monthly_payment: float,
    monthly_extra_amount: float,
) -> float | None:
    if loan_balance <= 0:
        return None

    total_budget = monthly_payment + monthly_extra_amount

    def difference(annual_return: float) -> float:
        common = dict(
            loan_balance=loan_balance,
            annual_interest_rate=annual_interest_rate,
            remaining_months=remaining_months,
            calculation_date=calculation_date,
            loan_end_date=loan_end_date,
            total_monthly_budget=total_budget,
            annual_investment_return=annual_return,
        )
        invest = simulate_strategy(
            **common,
            desired_mortgage_payment=monthly_payment,
        )
        repay = simulate_strategy(
            **common,
            desired_mortgage_payment=total_budget,
        )
        return invest["investment_value"] - repay["investment_value"]

    low, high = 0.0, 100.0
    low_difference = difference(low)
    high_difference = difference(high)

    if abs(high_difference - low_difference) < 0.005:
        return None
    if low_difference >= -0.005:
        return 0.0
    if high_difference <= 0:
        return None

    for _ in range(35):
        middle = (low + high) / 2
        if difference(middle) < 0:
            low = middle
        else:
            high = middle

    return round((low + high) / 2, 2)


def get_mortgage_vs_invest(
    db: Session,
    property_id: int,
    request: MortgageVsInvestRequest,
):
    property_record = (
        real_estate_repository
        .get_property_by_id(
            db,
            property_id,
        )
    )

    if property_record is None:
        return None

    calculation_date = date.today()

    loan_balance = float(
        property_record.loan_balance
    )

    annual_interest_rate = float(
        property_record.interest_rate
        or 0.0
    )

    monthly_payment = float(
        property_record.monthly_payment
    )

    stored_loan_end_date = (
        property_record.loan_end_date
    )

    remaining_months = (
        get_remaining_months(
            calculation_date,
            stored_loan_end_date,
        )
    )

    comparison_end_date = (
        stored_loan_end_date
        or add_months(
            calculation_date,
            remaining_months,
        )
    )

    baseline = simulate_strategy(
        loan_balance=loan_balance,
        annual_interest_rate=(
            annual_interest_rate
        ),
        remaining_months=(
            remaining_months
        ),
        calculation_date=(
            calculation_date
        ),
        loan_end_date=(
            comparison_end_date
        ),
        total_monthly_budget=(
            monthly_payment
        ),
        desired_mortgage_payment=(
            monthly_payment
        ),
        annual_investment_return=0.0,
    )

    if baseline["remaining_balance"] > 0.005:
        raise ValueError(
            "The recorded monthly mortgage payment does not repay "
            "the loan by the comparison end date. Update the loan "
            "balance, interest rate, monthly payment or end date."
        )

    baseline_interest = float(
        baseline["interest_paid"]
    )

    baseline_total_paid = (
        loan_balance
        + baseline_interest
    )

    monthly_extra_amount = float(
        request.monthly_extra_amount
    )

    hybrid_percentage = float(
        request
        .hybrid_mortgage_percentage
    )

    total_monthly_budget = (
        monthly_payment
        + monthly_extra_amount
    )

    break_even_return = find_break_even_return(
        loan_balance=loan_balance,
        annual_interest_rate=annual_interest_rate,
        remaining_months=remaining_months,
        calculation_date=calculation_date,
        loan_end_date=comparison_end_date,
        monthly_payment=monthly_payment,
        monthly_extra_amount=monthly_extra_amount,
    )

    comparisons = []

    for annual_return in (
        request
        .annual_investment_returns
    ):
        annual_return = float(
            annual_return
        )

        invest_only_result = (
            simulate_strategy(
                loan_balance=loan_balance,
                annual_interest_rate=(
                    annual_interest_rate
                ),
                remaining_months=(
                    remaining_months
                ),
                calculation_date=(
                    calculation_date
                ),
                loan_end_date=(
                    comparison_end_date
                ),
                total_monthly_budget=(
                    total_monthly_budget
                ),
                desired_mortgage_payment=(
                    monthly_payment
                ),
                annual_investment_return=(
                    annual_return
                ),
            )
        )

        repay_first_result = (
            simulate_strategy(
                loan_balance=loan_balance,
                annual_interest_rate=(
                    annual_interest_rate
                ),
                remaining_months=(
                    remaining_months
                ),
                calculation_date=(
                    calculation_date
                ),
                loan_end_date=(
                    comparison_end_date
                ),
                total_monthly_budget=(
                    total_monthly_budget
                ),
                desired_mortgage_payment=(
                    total_monthly_budget
                ),
                annual_investment_return=(
                    annual_return
                ),
            )
        )

        hybrid_mortgage_amount = (
            monthly_extra_amount
            * hybrid_percentage
            / 100
        )

        hybrid_investment_amount = (
            monthly_extra_amount
            - hybrid_mortgage_amount
        )

        hybrid_result = (
            simulate_strategy(
                loan_balance=loan_balance,
                annual_interest_rate=(
                    annual_interest_rate
                ),
                remaining_months=(
                    remaining_months
                ),
                calculation_date=(
                    calculation_date
                ),
                loan_end_date=(
                    comparison_end_date
                ),
                total_monthly_budget=(
                    total_monthly_budget
                ),
                desired_mortgage_payment=(
                    monthly_payment
                    + hybrid_mortgage_amount
                ),
                annual_investment_return=(
                    annual_return
                ),
            )
        )

        invest_only_value = float(
            invest_only_result[
                "investment_value"
            ]
        )

        outcomes = [
            {
                "strategy": (
                    "invest_only"
                ),
                "description": (
                    "Keep the standard "
                    "mortgage payment and "
                    "invest all additional "
                    "monthly cash."
                ),
                "mortgage_monthly_amount": (
                    monthly_payment
                ),
                "investment_monthly_amount": (
                    monthly_extra_amount
                ),
                "payoff_months": (
                    invest_only_result[
                        "payoff_months"
                    ]
                ),
                "payoff_date": (
                    invest_only_result[
                        "payoff_date"
                    ]
                ),
                "interest_paid": round(
                    invest_only_result[
                        "interest_paid"
                    ],
                    2,
                ),
                "interest_saved": 0.0,
                "investment_value_at_horizon": (
                    round(
                        invest_only_value,
                        2,
                    )
                ),
                "advantage_vs_invest_only": (
                    0.0
                ),
            },
            {
                "strategy": (
                    "repay_first"
                ),
                "description": (
                    "Use the full monthly "
                    "budget for the mortgage "
                    "until payoff, then invest "
                    "the full released budget."
                ),
                "mortgage_monthly_amount": (
                    total_monthly_budget
                ),
                "investment_monthly_amount": (
                    0.0
                ),
                "payoff_months": (
                    repay_first_result[
                        "payoff_months"
                    ]
                ),
                "payoff_date": (
                    repay_first_result[
                        "payoff_date"
                    ]
                ),
                "interest_paid": round(
                    repay_first_result[
                        "interest_paid"
                    ],
                    2,
                ),
                "interest_saved": round(
                    baseline_interest
                    - repay_first_result[
                        "interest_paid"
                    ],
                    2,
                ),
                "investment_value_at_horizon": (
                    round(
                        repay_first_result[
                            "investment_value"
                        ],
                        2,
                    )
                ),
                "advantage_vs_invest_only": (
                    round(
                        repay_first_result[
                            "investment_value"
                        ]
                        - invest_only_value,
                        2,
                    )
                ),
            },
            {
                "strategy": (
                    "hybrid"
                ),
                "description": (
                    "Split additional monthly "
                    "cash between mortgage "
                    "repayment and investing."
                ),
                "mortgage_monthly_amount": (
                    round(
                        monthly_payment
                        + hybrid_mortgage_amount,
                        2,
                    )
                ),
                "investment_monthly_amount": (
                    round(
                        hybrid_investment_amount,
                        2,
                    )
                ),
                "payoff_months": (
                    hybrid_result[
                        "payoff_months"
                    ]
                ),
                "payoff_date": (
                    hybrid_result[
                        "payoff_date"
                    ]
                ),
                "interest_paid": round(
                    hybrid_result[
                        "interest_paid"
                    ],
                    2,
                ),
                "interest_saved": round(
                    baseline_interest
                    - hybrid_result[
                        "interest_paid"
                    ],
                    2,
                ),
                "investment_value_at_horizon": (
                    round(
                        hybrid_result[
                            "investment_value"
                        ],
                        2,
                    )
                ),
                "advantage_vs_invest_only": (
                    round(
                        hybrid_result[
                            "investment_value"
                        ]
                        - invest_only_value,
                        2,
                    )
                ),
            },
        ]

        ranked_outcomes = sorted(
            outcomes,
            key=lambda item: (
                item[
                    "investment_value_at_horizon"
                ]
            ),
            reverse=True,
        )

        winner = ranked_outcomes[0]

        difference_to_second = (
            winner[
                "investment_value_at_horizon"
            ]
            - ranked_outcomes[1][
                "investment_value_at_horizon"
            ]
        )

        comparisons.append(
            {
                "annual_investment_return": (
                    round(
                        annual_return,
                        2,
                    )
                ),
                "invest_only": outcomes[0],
                "repay_first": outcomes[1],
                "hybrid": outcomes[2],
                "winner": (
                    winner["strategy"]
                ),
                "winner_value": (
                    winner[
                        "investment_value_at_horizon"
                    ]
                ),
                "difference_to_second": (
                    round(
                        difference_to_second,
                        2,
                    )
                ),
            }
        )

    return {
        "property_id": (
            property_record.id
        ),
        "property_name": (
            property_record.name
        ),
        "currency": (
            property_record.currency
        ),
        "monthly_extra_amount": round(
            monthly_extra_amount,
            2,
        ),
        "hybrid_mortgage_percentage": (
            round(
                hybrid_percentage,
                2,
            )
        ),
        "calculation_date": (
            calculation_date
        ),
        "comparison_end_date": (
            comparison_end_date
        ),
        "break_even_annual_return": break_even_return,
        "baseline": {
            "loan_balance": round(
                loan_balance,
                2,
            ),
            "annual_interest_rate": round(
                annual_interest_rate,
                4,
            ),
            "monthly_payment": round(
                monthly_payment,
                2,
            ),
            "remaining_months": (
                remaining_months
            ),
            "loan_end_date": (
                stored_loan_end_date
            ),
            "total_interest": round(
                baseline_interest,
                2,
            ),
            "total_paid": round(
                baseline_total_paid,
                2,
            ),
        },
        "comparisons": comparisons,
        "assumptions": [
            (
                "The mortgage interest rate "
                "stays constant for the full "
                "comparison period."
            ),
            (
                "Investment returns are "
                "modeled as constant nominal "
                "annual returns compounded "
                "monthly."
            ),
            (
                "The same total monthly cash "
                "budget is used by every "
                "strategy."
            ),
            (
                "After the mortgage is repaid, "
                "the released mortgage payment "
                "is invested until the original "
                "loan end date."
            ),
            (
                "Taxes, investment fees, "
                "insurance and early repayment "
                "fees are excluded."
            ),
        ],
    }
