"""add_transaction_commission

Revision ID: f0a350545d13
Revises: e86232aafddd
Create Date: 2026-08-09 22:23:23.216367

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f0a350545d13"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "e86232aafddd"
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
            "commission",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "transactions",
        "commission",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "transactions",
        "commission",
    )