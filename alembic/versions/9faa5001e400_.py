"""empty message

Revision ID: 9faa5001e400
Revises: 8a94638c5c4e, 8ea82bb18bfc
Create Date: 2024-08-08 08:58:25.599514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9faa5001e400'
down_revision: Union[str, None] = ('8a94638c5c4e', '8ea82bb18bfc')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
