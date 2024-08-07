"""merge 085de908c797 and 3ae61bbea328

Revision ID: ea8a695ec322
Revises: 3ae61bbea328
Create Date: 2024-08-07 04:35:06.441868

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea8a695ec322'
down_revision: Union[str, None] = '3ae61bbea328'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
