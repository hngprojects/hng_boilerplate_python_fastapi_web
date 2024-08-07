"""merge multiple heads

Revision ID: 4754043d011c
Revises: fb07cddb8fd2
Create Date: 2024-08-07 05:08:16.904442

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4754043d011c'
down_revision: Union[str, None] = 'fb07cddb8fd2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
