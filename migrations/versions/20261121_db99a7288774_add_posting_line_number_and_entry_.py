"""add posting line number and entry lookups

Revision ID: db99a7288774
Revises: 8bdadaf59469
Create Date: 2026-11-21 18:42:32.774226
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "db99a7288774"
down_revision: str | Sequence[str] | None = "8bdadaf59469"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_journal_entries_tenant_effective_at_id",
        "journal_entries",
        ["tenant_id", "effective_at", "id"],
    )
    op.create_unique_constraint(
        "uq_journal_entries_tenant_external_ref", "journal_entries", ["tenant_id", "external_ref"]
    )
    op.add_column("postings", sa.Column("line_number", sa.SmallInteger(), nullable=True))
    # numbers postings saved before this column existed; their original order is unknown
    op.execute(
        """
        UPDATE postings
        SET line_number = numbered.line_number
        FROM (
            SELECT id, row_number() OVER (PARTITION BY entry_id ORDER BY id) AS line_number
            FROM postings
        ) AS numbered
        WHERE postings.id = numbered.id
        """
    )
    op.alter_column("postings", "line_number", nullable=False)
    op.create_unique_constraint(
        "uq_postings_entry_line_number", "postings", ["entry_id", "line_number"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_postings_entry_line_number", "postings", type_="unique")
    op.drop_column("postings", "line_number")
    op.drop_constraint("uq_journal_entries_tenant_external_ref", "journal_entries", type_="unique")
    op.drop_index("ix_journal_entries_tenant_effective_at_id", table_name="journal_entries")
