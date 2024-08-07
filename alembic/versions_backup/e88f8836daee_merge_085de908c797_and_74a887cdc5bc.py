"""merge 085de908c797 and 74a887cdc5bc

Revision ID: e88f8836daee
Revises: 74a887cdc5bc
Create Date: 2024-08-07 04:36:56.495816

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e88f8836daee'
down_revision: Union[str, None] = '74a887cdc5bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
