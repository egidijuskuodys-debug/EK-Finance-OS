"""add_realized_profit

Revision ID: 6e1796bc33ee
Revises: e19239703e33
Create Date: 2026-08-06 01:49:29.215999

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6e1796bc33ee"
down_revision: Union[str, Sequence[str], None] = "e19239703e33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column(
            "realized_profit",
            sa.Float(),
            nullable=False,
            server_default="0",
        ),
    )

    op.alter_column(
        "transactions",
        "realized_profit",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column(
        "transactions",
        "realized_profit",
    )