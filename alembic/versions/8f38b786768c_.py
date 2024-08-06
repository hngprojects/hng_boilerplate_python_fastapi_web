"""empty message

Revision ID: 8f38b786768c
Revises: aeb162769644, ec23915c80e6
Create Date: 2024-08-06 07:56:06.598270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f38b786768c'
down_revision: Union[str, None] = ('aeb162769644', 'ec23915c80e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
