"""Recreate missing revision cc8bc6139578

Revision ID: 2244b5113efd
Revises: ff96e067c204
Create Date: 2024-08-08 03:46:56.475314

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2244b5113efd'
down_revision: Union[str, None] = 'ff96e067c204'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
