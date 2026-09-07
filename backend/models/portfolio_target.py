from sqlalchemy import (
    Column,
    Float,
    Integer,
    String,
    UniqueConstraint,
)

from database.db import Base


class PortfolioTarget(Base):
    __tablename__ = (
        "portfolio_targets"
    )

    __table_args__ = (
        UniqueConstraint(
            "dimension",
            "target_key",
            name=(
                "uq_portfolio_target_"
                "dimension_key"
            ),
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    dimension = Column(
        String(50),
        nullable=False,
        index=True,
    )

    target_key = Column(
        String(100),
        nullable=False,
        index=True,
    )

    target_percentage = Column(
        Float,
        nullable=False,
    )