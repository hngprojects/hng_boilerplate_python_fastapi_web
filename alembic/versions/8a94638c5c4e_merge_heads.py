"""Merge heads

Revision ID: 8a94638c5c4e
Revises: 3bd6f24777db, 8caa1a06240c
Create Date: 2024-08-08 06:06:15.452842

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a94638c5c4e'
down_revision: Union[str, None] = ('3bd6f24777db', '8caa1a06240c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
