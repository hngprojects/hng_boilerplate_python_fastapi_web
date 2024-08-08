"""Merge heads 2244b5113efd and acf9e7078f29

Revision ID: f0d5d76f254c
Revises: acf9e7078f29
Create Date: 2024-08-08 04:05:44.329493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f0d5d76f254c'
down_revision: Union[str, None] = 'acf9e7078f29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
