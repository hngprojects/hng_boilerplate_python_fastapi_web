"""empty message

Revision ID: ac6ee5ebdd31
Revises: 5977055d4cf1, 6d9c88b1af24
Create Date: 2024-08-08 01:53:34.743928

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ac6ee5ebdd31'
down_revision: Union[str, None] = ('5977055d4cf1', '6d9c88b1af24')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
