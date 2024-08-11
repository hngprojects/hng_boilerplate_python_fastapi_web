"""merge heads

Revision ID: e63f024c23eb
Revises: 0c0978bc2925, 3f455aaf9065
Create Date: 2024-08-10 11:54:28.435165

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e63f024c23eb'
down_revision: Union[str, None] = ('0c0978bc2925', '3f455aaf9065')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
