"""merge 085de908c797 and 6480079e527f

Revision ID: cf1826d7eaa7
Revises: 6480079e527f
Create Date: 2024-08-07 04:52:55.584727

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf1826d7eaa7'
down_revision: Union[str, None] = '6480079e527f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
