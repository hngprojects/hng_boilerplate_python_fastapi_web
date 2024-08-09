"""Merge heads 2244b5113efd and cc8bc6139578

Revision ID: 27e7513a6d1b
Revises: cc8bc6139578
Create Date: 2024-08-08 04:01:05.577084

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '27e7513a6d1b'
down_revision: Union[str, None] = 'cc8bc6139578'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass