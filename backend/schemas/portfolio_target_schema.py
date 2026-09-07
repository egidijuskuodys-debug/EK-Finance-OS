from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PortfolioTargetBase(BaseModel):
    dimension: str = Field(min_length=1, max_length=50)
    target_key: str = Field(min_length=1, max_length=100)
    target_percentage: float = Field(ge=0, le=100)


class PortfolioTargetCreate(PortfolioTargetBase):
    pass


class PortfolioTargetUpdate(BaseModel):
    dimension: Optional[str] = Field(
        default=None, min_length=1, max_length=50
    )
    target_key: Optional[str] = Field(
        default=None, min_length=1, max_length=100
    )
    target_percentage: Optional[float] = Field(
        default=None, ge=0, le=100
    )


class PortfolioTargetResponse(PortfolioTargetBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
