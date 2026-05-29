"""add announce_channel_id to guilds

Revision ID: a1b2c3d4e5f6
Revises: 497c4b6fca7d
Create Date: 2026-05-29 06:14:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '497c4b6fca7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add announce_channel_id column to guilds table
    op.add_column('guilds', sa.Column('announce_channel_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove announce_channel_id column from guilds table
    op.drop_column('guilds', 'announce_channel_id')
