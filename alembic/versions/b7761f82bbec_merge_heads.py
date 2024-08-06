"""Merge heads

Revision ID: b7761f82bbec
Revises: 1778dd5dc8a6, aeb162769644
Create Date: 2024-08-06 04:00:17.775283

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7761f82bbec'
down_revision: Union[str, None] = ('1778dd5dc8a6', 'aeb162769644')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
