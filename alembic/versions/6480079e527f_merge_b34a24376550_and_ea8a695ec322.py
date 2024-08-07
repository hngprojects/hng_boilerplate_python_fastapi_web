"""merge b34a24376550 and ea8a695ec322

Revision ID: 6480079e527f
Revises: ea8a695ec322
Create Date: 2024-08-07 04:37:15.851390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6480079e527f'
down_revision: Union[str, None] = 'ea8a695ec322'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
