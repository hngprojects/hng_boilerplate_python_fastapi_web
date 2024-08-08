"""Merge heads 2244b5113efd and 27e7513a6d1b

Revision ID: acf9e7078f29
Revises: 27e7513a6d1b
Create Date: 2024-08-08 04:04:48.124513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acf9e7078f29'
down_revision: Union[str, None] = '27e7513a6d1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
