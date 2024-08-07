"""merge b34a24376550 and e88f8836daee

Revision ID: 34e4df641250
Revises: e88f8836daee
Create Date: 2024-08-07 04:53:04.762914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34e4df641250'
down_revision: Union[str, None] = 'e88f8836daee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
