"""add username to users

Revision ID: 5d537ea2381c
Revises: e7cfa36143af
Create Date: 2026-09-06 01:53:46.755037

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5d537ea2381c"
down_revision: Union[str, Sequence[str], None] = "e7cfa36143af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("username", sa.String(), nullable=True),
    )

    op.execute(
        """
        UPDATE users
        SET username = 'User-' || id
        WHERE username IS NULL
        """
    )

    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column(
        "users",
        "username",
    )