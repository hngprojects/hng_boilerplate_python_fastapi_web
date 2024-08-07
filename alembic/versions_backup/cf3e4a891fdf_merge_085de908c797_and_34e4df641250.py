"""merge 085de908c797 and 34e4df641250

Revision ID: cf3e4a891fdf
Revises: 34e4df641250
Create Date: 2024-08-07 04:57:10.213759

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf3e4a891fdf'
down_revision: Union[str, None] = '34e4df641250'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
