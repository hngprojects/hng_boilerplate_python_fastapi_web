"""merge b34a24376550 and d96ccae1d44f

Revision ID: 3ae61bbea328
Revises: d96ccae1d44f
Create Date: 2024-08-07 04:31:37.801498

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ae61bbea328'
down_revision: Union[str, None] = 'd96ccae1d44f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
