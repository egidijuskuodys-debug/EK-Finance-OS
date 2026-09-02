"""add_import_history

Revision ID: b68b844582b7
Revises: f90ae9c0296c

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b68b844582b7"
down_revision: Union[str, Sequence[str], None] = "f90ae9c0296c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "import_history",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "broker",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "file_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "file_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "imported_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "transactions_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "dividends_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "cash_movements_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "positions_count",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "duplicates_skipped",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "error_message",
            sa.String(length=1000),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_import_history_id"),
        "import_history",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_import_history_broker"),
        "import_history",
        ["broker"],
        unique=False,
    )

    op.create_index(
        op.f("ix_import_history_file_hash"),
        "import_history",
        ["file_hash"],
        unique=True,
    )

    op.create_index(
        op.f("ix_import_history_imported_at"),
        "import_history",
        ["imported_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_import_history_imported_at"),
        table_name="import_history",
    )

    op.drop_index(
        op.f("ix_import_history_file_hash"),
        table_name="import_history",
    )

    op.drop_index(
        op.f("ix_import_history_broker"),
        table_name="import_history",
    )

    op.drop_index(
        op.f("ix_import_history_id"),
        table_name="import_history",
    )

    op.drop_table("import_history")