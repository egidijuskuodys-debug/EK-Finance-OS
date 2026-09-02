from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class DividendBase(BaseModel):
    investment_id: int = Field(gt=0)

    payment_date: date

    gross_amount: float = Field(gt=0)

    tax_amount: float = Field(
        default=0,
        ge=0,
    )

    net_amount: Optional[float] = Field(
        default=None,
        ge=0,
    )

    currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=10,
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
    )

    @model_validator(mode="after")
    def calculate_net_amount(self):
        calculated_net = (
            self.gross_amount
            - self.tax_amount
        )

        if calculated_net < 0:
            raise ValueError(
                "Tax amount cannot exceed gross amount."
            )

        if self.net_amount is None:
            self.net_amount = round(
                calculated_net,
                2,
            )

        return self


class DividendCreate(DividendBase):
    pass


class DividendUpdate(BaseModel):
    investment_id: Optional[int] = Field(
        default=None,
        gt=0,
    )

    payment_date: Optional[date] = None

    gross_amount: Optional[float] = Field(
        default=None,
        gt=0,
    )

    tax_amount: Optional[float] = Field(
        default=None,
        ge=0,
    )

    net_amount: Optional[float] = Field(
        default=None,
        ge=0,
    )

    currency: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=10,
    )

    notes: Optional[str] = Field(
        default=None,
        max_length=500,
    )


class DividendResponse(DividendBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )