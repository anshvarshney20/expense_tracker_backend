"""add currency to users

Revision ID: a1b2c3d4e5f6
Revises: ed4c56c579d9
Create Date: 2026-02-25 08:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'ed4c56c579d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add currency column to users table with a server default
    op.add_column('users', sa.Column('currency', sa.String(length=10), nullable=False, server_default='USD'))


def downgrade() -> None:
    op.drop_column('users', 'currency')
