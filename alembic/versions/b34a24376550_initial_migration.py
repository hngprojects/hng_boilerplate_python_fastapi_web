"""initial migration

Revision ID: b34a24376550
Revises: 854472eb449d
Create Date: 2024-08-06 11:28:56.645803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b34a24376550'
down_revision: Union[str, None] = '854472eb449d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
