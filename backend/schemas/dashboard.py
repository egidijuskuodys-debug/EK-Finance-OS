from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_positions: int
    total_quantity: float
    total_invested: float