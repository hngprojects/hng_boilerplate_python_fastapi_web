"""Merge heads

Revision ID: 71d054d194e6
Revises: 1b25d20e2a33, 79bf3583c6d3
Create Date: 2024-07-30 00:49:08.369058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71d054d194e6'
down_revision: Union[str, None] = ('1b25d20e2a33', '79bf3583c6d3')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
