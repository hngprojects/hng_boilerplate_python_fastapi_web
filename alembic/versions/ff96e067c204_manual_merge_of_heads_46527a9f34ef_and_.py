"""Manual merge of heads 46527a9f34ef and 8caa1a06240c

Revision ID: ff96e067c204
Revises: 46527a9f34ef
Create Date: 2024-08-08 03:40:20.982705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff96e067c204'
down_revision: Union[str, None] = ('46527a9f34ef', '8caa1a06240c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
