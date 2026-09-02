"""add_current_price_and_asset_type

Revision ID: 39d008a9ae73
Revises:
Create Date: 2026-08-04 23:48:36.808294

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "39d008a9ae73"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "investments",
        sa.Column(
            "asset_type",
            sa.String(length=50),
            nullable=False,
            server_default="Stock",
        ),
    )

    op.add_column(
        "investments",
        sa.Column(
            "current_price",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "investments",
        "asset_type",
        server_default=None,
    )

    op.alter_column(
        "investments",
        "current_price",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("investments", "current_price")
    op.drop_column("investments", "asset_type")