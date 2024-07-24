"""empty message

Revision ID: a1390601d956
Revises: 2a8bed88c439, 910a7c73019a
Create Date: 2024-07-24 22:40:40.914104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1390601d956'
down_revision: Union[str, None] = ('2a8bed88c439', '910a7c73019a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
