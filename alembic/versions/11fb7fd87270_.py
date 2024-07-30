"""empty message

Revision ID: 11fb7fd87270
Revises: 9457e53a7c29, d0fdcf651c1c
Create Date: 2024-07-30 18:38:44.026079

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11fb7fd87270'
down_revision: Union[str, None] = ('9457e53a7c29', 'd0fdcf651c1c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
