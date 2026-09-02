"""add_dividends

Revision ID: f90ae9c0296c
Revises: 3f76c1398d42
Create Date: 2026-08-06 22:08:22.038114

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f90ae9c0296c"
down_revision: Union[str, Sequence[str], None] = "3f76c1398d42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create dividends table."""

    op.create_table(
        "dividends",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "investment_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "payment_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "gross_amount",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "tax_amount",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "net_amount",
            sa.Float(),
            nullable=False,
        ),
        sa.Column(
            "currency",
            sa.String(length=10),
            nullable=False,
        ),
        sa.Column(
            "notes",
            sa.String(length=500),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["investment_id"],
            ["investments.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_dividends_id"),
        "dividends",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_dividends_investment_id"),
        "dividends",
        ["investment_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_dividends_payment_date"),
        "dividends",
        ["payment_date"],
        unique=False,
    )


def downgrade() -> None:
    """Remove dividends table."""

    op.drop_index(
        op.f("ix_dividends_payment_date"),
        table_name="dividends",
    )

    op.drop_index(
        op.f("ix_dividends_investment_id"),
        table_name="dividends",
    )

    op.drop_index(
        op.f("ix_dividends_id"),
        table_name="dividends",
    )

    op.drop_table("dividends")