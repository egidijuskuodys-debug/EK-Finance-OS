"""add fx rate to transactions

Revision ID: c0003091f852
Revises: f0a350545d13
Create Date: 2026-09-01 18:14:36.088845

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0003091f852"
down_revision: Union[str, Sequence[str], None] = (
    "f0a350545d13"
)
branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None
depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "transactions",
        sa.Column(
            "fx_rate",
            sa.Float(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "transactions",
        "fx_rate",
    )