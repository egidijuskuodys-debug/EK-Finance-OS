from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.financial_independence import (
    FinancialIndependenceResponse,
)
from schemas.net_worth_projection import (
    NetWorthProjectionResponse,
)
from services.analytics_service import (
    get_allocation,
    get_dividend_summary,
    get_dividends_by_investment,
    get_dividends_by_year,
    get_performance,
    get_summary,
    recalculate_portfolio,
)
from services.financial_independence_service import (
    get_financial_independence_projection,
)
from services.monthly_investment_plan_service import (
    get_monthly_investment_plan,
)
from services.net_worth_projection_service import (
    get_net_worth_projection,
)
from services.performance_breakdown_service import (
    get_performance_breakdown,
)
from services.performance_service import (
    get_portfolio_xirr,
)
from services.portfolio_actions_service import (
    get_portfolio_actions,
)
from services.portfolio_contribution_service import (
    get_contribution_plan,
)
from services.portfolio_health_service import (
    get_portfolio_health,
)
from services.portfolio_history_service import (
    get_portfolio_history,
)
from services.portfolio_insights_service import (
    get_portfolio_insights,
)
from services.portfolio_projection_service import (
    get_portfolio_projection,
)
from services.portfolio_rebalancing_service import (
    get_portfolio_rebalancing,
)
from services.risk_service import (
    get_portfolio_risk,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("/summary")
def portfolio_summary(
    db: Session = Depends(
        get_db
    ),
):
    return get_summary(
        db
    )


@router.get("/allocation")
def portfolio_allocation(
    db: Session = Depends(
        get_db
    ),
):
    return get_allocation(
        db
    )


@router.get("/risk")
def portfolio_risk(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_risk(
        db
    )


@router.get("/health")
def portfolio_health(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_health(
        db
    )


@router.get("/insights")
def portfolio_insights(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_insights(
        db
    )


@router.get("/actions")
def portfolio_actions(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_actions(
        db
    )


@router.get("/rebalancing")
def portfolio_rebalancing(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_rebalancing(
        db
    )


@router.get("/contribution-plan")
def portfolio_contribution_plan(
    amount: float = Query(
        default=1000.0,
        gt=0,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return get_contribution_plan(
        db,
        amount,
    )


@router.get("/monthly-investment-plan")
def monthly_investment_plan(
    monthly_amount: float = Query(
        default=1000.0,
        gt=0,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return get_monthly_investment_plan(
        db=db,
        monthly_amount=(
            monthly_amount
        ),
    )


@router.get("/projection")
def portfolio_projection(
    monthly_contribution: float = Query(
        default=1000.0,
        ge=0,
    ),
    annual_return_percent: float = Query(
        default=7.0,
        gt=-100,
        le=100,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_projection(
        db=db,
        monthly_contribution=(
            monthly_contribution
        ),
        annual_return_percent=(
            annual_return_percent
        ),
    )


@router.get(
    "/net-worth-projection",
    response_model=(
        NetWorthProjectionResponse
    ),
)
def net_worth_projection(
    monthly_contribution: float = Query(
        default=1000.0,
        ge=0,
    ),
    annual_return_percent: float = Query(
        default=7.0,
        gt=-100,
        le=100,
    ),
    annual_property_growth: float = Query(
        default=2.0,
        gt=-100,
        le=100,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return get_net_worth_projection(
        db=db,
        monthly_contribution=(
            monthly_contribution
        ),
        annual_return_percent=(
            annual_return_percent
        ),
        annual_property_growth=(
            annual_property_growth
        ),
    )


@router.get(
    "/financial-independence",
    response_model=(
        FinancialIndependenceResponse
    ),
)
def financial_independence(
    monthly_income_target: float = Query(
        default=1000.0,
        gt=0,
    ),
    withdrawal_rate_percent: float = Query(
        default=4.0,
        gt=0,
        le=100,
    ),
    monthly_contribution: float = Query(
        default=1000.0,
        ge=0,
    ),
    annual_return_percent: float = Query(
        default=7.0,
        gt=-100,
        le=100,
    ),
    annual_property_growth: float = Query(
        default=2.0,
        gt=-100,
        le=100,
    ),
    current_age: int = Query(
        default=45,
        ge=0,
        le=120,
    ),
    db: Session = Depends(
        get_db
    ),
):
    return (
        get_financial_independence_projection(
            db=db,
            monthly_income_target=(
                monthly_income_target
            ),
            withdrawal_rate_percent=(
                withdrawal_rate_percent
            ),
            monthly_contribution=(
                monthly_contribution
            ),
            annual_return_percent=(
                annual_return_percent
            ),
            annual_property_growth=(
                annual_property_growth
            ),
            current_age=current_age,
        )
    )


@router.get("/performance")
def portfolio_performance(
    db: Session = Depends(
        get_db
    ),
):
    return get_performance(
        db
    )


@router.get("/performance-breakdown")
def portfolio_performance_breakdown(
    db: Session = Depends(
        get_db
    ),
):
    return get_performance_breakdown(
        db
    )


@router.get("/xirr")
def portfolio_xirr(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_xirr(
        db
    )


@router.get("/portfolio-history")
def portfolio_history(
    db: Session = Depends(
        get_db
    ),
):
    return get_portfolio_history(
        db
    )


@router.get("/dividends/summary")
def dividend_summary(
    db: Session = Depends(
        get_db
    ),
):
    return get_dividend_summary(
        db
    )


@router.get("/dividends/by-year")
def dividends_by_year(
    db: Session = Depends(
        get_db
    ),
):
    return get_dividends_by_year(
        db
    )


@router.get("/dividends/by-investment")
def dividends_by_investment(
    db: Session = Depends(
        get_db
    ),
):
    return get_dividends_by_investment(
        db
    )


@router.post("/recalculate")
def recalculate(
    db: Session = Depends(
        get_db
    ),
):
    return recalculate_portfolio(
        db
    )