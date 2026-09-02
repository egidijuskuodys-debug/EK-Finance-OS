"""add fx rate to dividends

Revision ID: 26e822426eeb
Revises: c0003091f852

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "26e822426eeb"
down_revision: Union[str, Sequence[str], None] = (
    "c0003091f852"
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
        "dividends",
        sa.Column(
            "fx_rate",
            sa.Float(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        "dividends",
        "fx_rate",
    )