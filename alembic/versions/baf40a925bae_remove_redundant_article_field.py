"""Remove redundant article field

Revision ID: baf40a925bae
Revises: b98b56f95aeb
Create Date: 2024-07-22 00:17:29.946994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'baf40a925bae'
down_revision: Union[str, None] = 'b98b56f95aeb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
