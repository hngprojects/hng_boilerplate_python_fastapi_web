"""empty message

Revision ID: 299ab5d402fc
Revises: 224b03e9169c, 44f7da26ee88
Create Date: 2024-08-08 18:59:46.314362

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '299ab5d402fc'
down_revision: Union[str, None] = ('224b03e9169c', '44f7da26ee88')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass