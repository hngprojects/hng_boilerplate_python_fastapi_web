"""empty message

Revision ID: b98b56f95aeb
Revises: 534047ee3520, f2dab3932415
Create Date: 2024-07-22 00:17:14.165495

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b98b56f95aeb'
down_revision: Union[str, None] = ('534047ee3520', 'f2dab3932415')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
