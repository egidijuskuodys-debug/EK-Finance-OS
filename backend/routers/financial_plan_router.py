from fastapi import (
    APIRouter,
    Depends,
)
from sqlalchemy.orm import Session

from database.db import get_db
from schemas.financial_plan import (
    FinancialPlanRequest,
    FinancialPlanResponse,
)
from services.dashboard_service import (
    get_dashboard,
)
from services.financial_plan_service import (
    build_financial_plan,
)


router = APIRouter(
    prefix="/financial-plan",
    tags=["Financial Plan"],
)


@router.post(
    "/",
    response_model=FinancialPlanResponse,
)
def calculate_financial_plan(
    request: FinancialPlanRequest,
    db: Session = Depends(get_db),
):
    dashboard = get_dashboard(db)

    return build_financial_plan(
        request=request,
        current_investment_wealth=(
            dashboard["total_wealth"]
        ),
    )