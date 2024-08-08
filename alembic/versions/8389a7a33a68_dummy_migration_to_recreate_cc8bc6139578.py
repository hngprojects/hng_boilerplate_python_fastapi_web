"""Dummy migration to recreate cc8bc6139578

Revision ID: 8389a7a33a68
Revises: 2244b5113efd
Create Date: 2024-08-08 03:56:34.742443

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc8bc6139578'
down_revision: Union[str, None] = 'ff96e067c204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
