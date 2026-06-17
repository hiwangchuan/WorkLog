"""team and attachment upgrade fields"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_team_attachment_upgrade"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("teams", sa.Column("status", sa.String(length=30), nullable=True))
    op.execute("UPDATE teams SET status = 'active' WHERE status IS NULL")
    op.alter_column("teams", "status", nullable=False, server_default="active")

    op.add_column("attachments", sa.Column("storage_path", sa.String(length=800), nullable=True))
    op.add_column("attachments", sa.Column("mime_type", sa.String(length=160), nullable=True))
    op.add_column("attachments", sa.Column("summary", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("attachments", "summary")
    op.drop_column("attachments", "mime_type")
    op.drop_column("attachments", "storage_path")
    op.drop_column("teams", "status")
