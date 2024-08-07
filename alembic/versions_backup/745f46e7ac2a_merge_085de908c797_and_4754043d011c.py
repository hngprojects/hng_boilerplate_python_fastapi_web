"""Merge 085de908c797 and 4754043d011c

Revision ID: 745f46e7ac2a
Revises: 085de908c797, 4754043d011c
Create Date: 2024-08-07 05:26:11.183855

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '745f46e7ac2a'
down_revision: Union[str, Sequence[str], None] = ('085de908c797', '4754043d011c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
