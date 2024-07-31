"""Recreate missing revision dce3ec9fb4b9

Revision ID: a898bf25a528
Revises: 5f9d01dc6cc9
Create Date: 2024-07-30 22:16:15.186471

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a898bf25a528'
down_revision: Union[str, None] = '5f9d01dc6cc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
