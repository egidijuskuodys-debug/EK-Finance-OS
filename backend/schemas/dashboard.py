from pydantic import BaseModel


class DashboardAllocationItem(BaseModel):
    name: str
    value: float
    percentage: float


class DashboardPositionItem(BaseModel):
    ticker: str
    asset_type: str
    current_value: float
    profit_loss: float
    profit_loss_percent: float


class DashboardResponse(BaseModel):
    total_positions: int
    total_quantity: float

    portfolio_value: float
    total_invested: float

    unrealized_profit: float
    unrealized_profit_percent: float

    realized_profit: float

    dividend_net: float

    total_profit: float
    total_return_percent: float

    best_position: str | None
    worst_position: str | None

    base_currency: str

    asset_allocation: list[
        DashboardAllocationItem
    ]

    top_positions: list[
        DashboardPositionItem
    ]