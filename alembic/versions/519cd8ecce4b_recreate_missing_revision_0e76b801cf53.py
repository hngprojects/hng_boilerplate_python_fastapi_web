"""Recreate missing revision 0e76b801cf53

Revision ID: 519cd8ecce4b
Revises: 87280d61ce24
Create Date: 2024-07-29 13:41:39.954936

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '519cd8ecce4b'
down_revision: Union[str, None] = '87280d61ce24'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
