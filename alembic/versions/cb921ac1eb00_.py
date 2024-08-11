"""empty message

Revision ID: cb921ac1eb00
Revises: c9d13f346b57, e63f024c23eb
Create Date: 2024-08-11 12:23:39.081974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb921ac1eb00'
down_revision: Union[str, None] = ('c9d13f346b57', 'e63f024c23eb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
