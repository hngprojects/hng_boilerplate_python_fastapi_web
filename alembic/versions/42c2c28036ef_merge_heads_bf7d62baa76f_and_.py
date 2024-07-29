"""Merge heads bf7d62baa76f and cceffcebcee6

Revision ID: 42c2c28036ef
Revises: bf7d62baa76f, cceffcebcee6
Create Date: 2024-07-29 14:09:18.289448

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42c2c28036ef'
down_revision: Union[str, None] = ('bf7d62baa76f', 'cceffcebcee6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
