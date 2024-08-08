"""Merge heads 2244b5113efd and f0d5d76f254c

Revision ID: c1012aa6f30c
Revises: f0d5d76f254c
Create Date: 2024-08-08 04:06:51.988917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1012aa6f30c'
down_revision: Union[str, None] = 'f0d5d76f254c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
