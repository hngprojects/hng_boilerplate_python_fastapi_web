"""Merge heads

Revision ID: 836938cb4ce1
Revises: b7761f82bbec, bb0905b42300
Create Date: 2024-08-06 10:07:46.475250

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '836938cb4ce1'
down_revision: Union[str, None] = ('b7761f82bbec', 'bb0905b42300')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
