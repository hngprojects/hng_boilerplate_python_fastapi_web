"""Merge heads 0022063144a8 and 42c2c28036ef

Revision ID: 2590f4ea69fb
Revises: 0022063144a8, 42c2c28036ef
Create Date: 2024-07-29 15:23:57.260594

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2590f4ea69fb'
down_revision: Union[str, None] = ('0022063144a8', '42c2c28036ef')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
