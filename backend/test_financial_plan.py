import pytest
from pydantic import ValidationError

from schemas.financial_plan import (
    FinancialPlanRequest,
)
from services.financial_plan_service import (
    build_financial_plan,
    calculate_future_value,
)


def test_budget_is_split_between_investment_and_mortgage():
    request = FinancialPlanRequest(
        monthly_budget=1000,
        mortgage_share_percent=20,
        expected_etf_return_percent=7,
    )

    plan = build_financial_plan(
        request=request,
        current_investment_wealth=25000,
    )

    assert plan.monthly_budget == pytest.approx(
        1000
    )

    assert plan.monthly_mortgage_amount == pytest.approx(
        200
    )

    assert plan.monthly_investment_amount == pytest.approx(
        800
    )

    assert plan.mortgage_share_percent == pytest.approx(
        20
    )

    assert plan.investment_share_percent == pytest.approx(
        80
    )

    assert plan.annual_investment_amount == pytest.approx(
        9600
    )


def test_zero_mortgage_share_allocates_all_money_to_investments():
    request = FinancialPlanRequest(
        monthly_budget=1000,
        mortgage_share_percent=0,
        expected_etf_return_percent=7,
    )

    plan = build_financial_plan(
        request=request,
        current_investment_wealth=25000,
    )

    assert plan.monthly_mortgage_amount == pytest.approx(
        0
    )

    assert plan.monthly_investment_amount == pytest.approx(
        1000
    )

    assert plan.investment_share_percent == pytest.approx(
        100
    )

    assert len(plan.actions) == 1

    assert plan.actions[0].action == "INVEST"


def test_full_mortgage_share_allocates_no_money_to_investments():
    request = FinancialPlanRequest(
        monthly_budget=1000,
        mortgage_share_percent=100,
        expected_etf_return_percent=7,
    )

    plan = build_financial_plan(
        request=request,
        current_investment_wealth=25000,
    )

    assert plan.monthly_mortgage_amount == pytest.approx(
        1000
    )

    assert plan.monthly_investment_amount == pytest.approx(
        0
    )

    assert plan.investment_share_percent == pytest.approx(
        0
    )

    assert plan.annual_investment_amount == pytest.approx(
        0
    )

    assert len(plan.actions) == 1

    assert plan.actions[0].action == "MORTGAGE"


def test_zero_return_projection_has_no_investment_growth():
    future_value = calculate_future_value(
        current_value=25000,
        monthly_contribution=1000,
        annual_return_percent=0,
        years=5,
    )

    assert future_value == pytest.approx(
        85000
    )


def test_positive_return_projection_creates_growth():
    request = FinancialPlanRequest(
        monthly_budget=1000,
        mortgage_share_percent=20,
        expected_etf_return_percent=7,
        projection_years=[
            1,
            5,
            10,
        ],
    )

    plan = build_financial_plan(
        request=request,
        current_investment_wealth=25000,
    )

    assert len(plan.projections) == 3

    five_year_projection = next(
        projection
        for projection in plan.projections
        if projection.years == 5
    )

    assert (
        five_year_projection
        .projected_investment_value
        >
        (
            plan.current_investment_wealth
            + five_year_projection
            .additional_invested
        )
    )

    assert (
        five_year_projection
        .estimated_growth
        > 0
    )


def test_projection_years_are_sorted_and_duplicates_removed():
    request = FinancialPlanRequest(
        monthly_budget=1000,
        mortgage_share_percent=20,
        expected_etf_return_percent=7,
        projection_years=[
            10,
            1,
            5,
            5,
        ],
    )

    plan = build_financial_plan(
        request=request,
        current_investment_wealth=25000,
    )

    assert [
        projection.years
        for projection in plan.projections
    ] == [
        1,
        5,
        10,
    ]


def test_invalid_monthly_budget_is_rejected():
    with pytest.raises(
        ValidationError,
    ):
        FinancialPlanRequest(
            monthly_budget=0,
            mortgage_share_percent=20,
        )


def test_invalid_mortgage_share_is_rejected():
    with pytest.raises(
        ValidationError,
    ):
        FinancialPlanRequest(
            monthly_budget=1000,
            mortgage_share_percent=101,
        )


def test_plan_creates_investment_and_mortgage_actions():
    request = FinancialPlanRequest(
        monthly_budget=1000,
        mortgage_share_percent=20,
        expected_etf_return_percent=7,
    )

    plan = build_financial_plan(
        request=request,
        current_investment_wealth=25000,
    )

    assert len(plan.actions) == 2

    assert plan.actions[0].action == "INVEST"

    assert plan.actions[0].monthly_amount == pytest.approx(
        800
    )

    assert plan.actions[1].action == "MORTGAGE"

    assert plan.actions[1].monthly_amount == pytest.approx(
        200
    )