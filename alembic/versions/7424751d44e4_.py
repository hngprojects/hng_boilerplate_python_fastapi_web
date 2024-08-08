"""empty message

Revision ID: 7424751d44e4
Revises: 46527a9f34ef, 8caa1a06240c
Create Date: 2024-08-08 03:14:54.087197

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7424751d44e4'
down_revision: Union[str, None] = ('46527a9f34ef', '8caa1a06240c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
