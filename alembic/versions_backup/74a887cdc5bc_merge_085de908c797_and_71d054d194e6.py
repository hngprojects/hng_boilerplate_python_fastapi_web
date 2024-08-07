"""merge 085de908c797 and 71d054d194e6

Revision ID: 74a887cdc5bc
Revises: 71d054d194e6
Create Date: 2024-08-07 04:31:23.078206

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74a887cdc5bc'
down_revision: Union[str, None] = '71d054d194e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
