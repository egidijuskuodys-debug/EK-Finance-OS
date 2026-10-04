from unittest.mock import patch

from services.financial_independence_service import (
    get_financial_independence_projection,
)


def build_net_worth_projection():
    return {
        "currency": "EUR",
        "starting_investment_value": 25000.0,
        "starting_real_estate_equity": 20000.0,
        "starting_net_worth": 45000.0,
        "yearly_projection": [
            {
                "year": 0,
                "investment_value": 25000.0,
                "real_estate_value": 70000.0,
                "real_estate_loan_balance": 50000.0,
                "real_estate_equity": 20000.0,
                "net_worth": 45000.0,
            },
            {
                "year": 1,
                "investment_value": 40000.0,
                "real_estate_value": 71400.0,
                "real_estate_loan_balance": 48000.0,
                "real_estate_equity": 23400.0,
                "net_worth": 63400.0,
            },
            {
                "year": 5,
                "investment_value": 100000.0,
                "real_estate_value": 77285.0,
                "real_estate_loan_balance": 40000.0,
                "real_estate_equity": 37285.0,
                "net_worth": 137285.0,
            },
            {
                "year": 10,
                "investment_value": 200000.0,
                "real_estate_value": 85330.0,
                "real_estate_loan_balance": 25000.0,
                "real_estate_equity": 60330.0,
                "net_worth": 260330.0,
            },
            {
                "year": 15,
                "investment_value": 320000.0,
                "real_estate_value": 94211.0,
                "real_estate_loan_balance": 0.0,
                "real_estate_equity": 94211.0,
                "net_worth": 414211.0,
            },
        ],
    }


def build_real_estate_summary(
    monthly_cash_flow=0.0,
):
    return {
        "properties_count": 1,
        "total_current_value": 70000.0,
        "total_loan_balance": 50000.0,
        "total_equity": 20000.0,
        "total_monthly_rent": 400.0,
        "total_monthly_expenses": 20.0,
        "total_monthly_loan_payments": 330.0,
        "total_monthly_cash_flow": (
            monthly_cash_flow
        ),
        "total_annual_cash_flow": (
            monthly_cash_flow
            * 12
        ),
        "currency": "EUR",
    }


def calculate_projection(
    mock_projection,
    mock_real_estate_summary,
    monthly_cash_flow=0.0,
):
    mock_projection.return_value = (
        build_net_worth_projection()
    )

    mock_real_estate_summary.return_value = (
        build_real_estate_summary(
            monthly_cash_flow
        )
    )

    return (
        get_financial_independence_projection(
            db=None,
            monthly_income_target=1000,
            withdrawal_rate_percent=4,
            monthly_contribution=1000,
            annual_return_percent=7,
            annual_property_growth=2,
            current_age=45,
        )
    )


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_required_capital_without_rental_cash_flow(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
    )

    assert result["required_capital"] == 300000.0
    assert result["rental_monthly_cash_flow"] == 0.0


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_fi_uses_investment_capital_not_total_net_worth(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
    )

    assert result["current_fi_capital"] == 25000.0

    assert (
        result["investment_monthly_passive_income"]
        == 83.33
    )

    assert (
        result["current_monthly_passive_income"]
        == 83.33
    )

    assert result["remaining_gap"] == 275000.0
    assert result["progress_percent"] == 8.33


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_real_estate_equity_is_not_counted_as_fi_capital(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
    )

    first_point = result["yearly_projection"][0]

    assert first_point["investment_value"] == 25000.0
    assert first_point["net_worth"] == 45000.0

    assert (
        first_point["investment_monthly_passive_income"]
        == 83.33
    )


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_rental_cash_flow_reduces_required_investment_capital(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
        monthly_cash_flow=200.0,
    )

    assert result["rental_monthly_cash_flow"] == 200.0

    assert (
        result["investment_income_target"]
        == 800.0
    )

    assert (
        result["required_capital"]
        == 240000.0
    )


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_total_passive_income_includes_rental_cash_flow(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
        monthly_cash_flow=200.0,
    )

    assert (
        result["investment_monthly_passive_income"]
        == 83.33
    )

    assert (
        result["current_monthly_passive_income"]
        == 283.33
    )


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_goal_uses_investment_capital_after_rental_income(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
        monthly_cash_flow=200.0,
    )

    assert result["years_to_goal"] == 15
    assert result["projected_age_at_goal"] == 60

    year_10 = next(
        point
        for point in result["yearly_projection"]
        if point["year"] == 10
    )

    assert year_10["investment_value"] == 200000.0
    assert year_10["target_reached"] is False

    year_15 = next(
        point
        for point in result["yearly_projection"]
        if point["year"] == 15
    )

    assert year_15["investment_value"] == 320000.0
    assert year_15["target_reached"] is True


@patch(
    "services.financial_independence_service."
    "get_real_estate_summary"
)
@patch(
    "services.financial_independence_service."
    "get_net_worth_projection"
)
def test_rental_cash_flow_cannot_increase_required_capital(
    mock_projection,
    mock_real_estate_summary,
):
    result = calculate_projection(
        mock_projection,
        mock_real_estate_summary,
        monthly_cash_flow=-100.0,
    )

    assert result["rental_monthly_cash_flow"] == -100.0

    assert (
        result["investment_income_target"]
        == 1100.0
    )

    assert (
        result["required_capital"]
        == 330000.0
    )