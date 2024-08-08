"""empty message

Revision ID: fd592d30f9df
Revises: 46527a9f34ef
Create Date: 2024-08-08 05:31:16.310295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd592d30f9df'
down_revision: Union[str, None] = '46527a9f34ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
