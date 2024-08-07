"""merge b34a24376550 and cf1826d7eaa7

Revision ID: fb07cddb8fd2
Revises: cf1826d7eaa7
Create Date: 2024-08-07 04:57:23.086670

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb07cddb8fd2'
down_revision: Union[str, None] = 'cf1826d7eaa7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
