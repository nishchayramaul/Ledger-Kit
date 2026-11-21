"""add posting columns

Revision ID: 8bdadaf59469
Revises: 4a360df5462e
Create Date: 2026-11-21 17:33:08.859630
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8bdadaf59469"
down_revision: str | Sequence[str] | None = "4a360df5462e"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("postings", sa.Column("entry_id", sa.Uuid(), nullable=False))
    op.add_column("postings", sa.Column("account_id", sa.Uuid(), nullable=False))
    op.add_column("postings", sa.Column("direction", sa.Text(), nullable=False))
    op.add_column("postings", sa.Column("amount_minor", sa.BigInteger(), nullable=False))
    op.add_column("postings", sa.Column("currency", sa.CHAR(3), nullable=False))
    op.create_foreign_key(
        "fk_postings_entry_id", "postings", "journal_entries", ["entry_id"], ["id"]
    )
    op.create_foreign_key("fk_postings_account_id", "postings", "accounts", ["account_id"], ["id"])
    op.create_check_constraint(
        "ck_postings_direction", "postings", "direction IN ('debit', 'credit')"
    )
    op.create_check_constraint("ck_postings_amount_positive", "postings", "amount_minor > 0")
    op.create_index("ix_postings_entry_id", "postings", ["entry_id"])
    op.create_index("ix_postings_account_id", "postings", ["account_id"])


def downgrade() -> None:
    op.drop_index("ix_postings_account_id", table_name="postings")
    op.drop_index("ix_postings_entry_id", table_name="postings")
    op.drop_column("postings", "currency")
    op.drop_column("postings", "amount_minor")
    op.drop_column("postings", "direction")
    op.drop_column("postings", "account_id")
    op.drop_column("postings", "entry_id")
