"""add_market_ticker

Revision ID: e19239703e33
Revises: 39d008a9ae73
Create Date: 2026-08-05 01:16:48.778898

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e19239703e33"
down_revision: Union[str, Sequence[str], None] = "39d008a9ae73"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "investments",
        sa.Column(
            "market_ticker",
            sa.String(length=30),
            nullable=True,
        ),
    )

    # Esamiems įrašams nukopijuojame ticker reikšmę
    op.execute(
        """
        UPDATE investments
        SET market_ticker = ticker
        """
    )

    op.alter_column(
        "investments",
        "market_ticker",
        existing_type=sa.String(length=30),
        nullable=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "investments",
        "market_ticker",
    )