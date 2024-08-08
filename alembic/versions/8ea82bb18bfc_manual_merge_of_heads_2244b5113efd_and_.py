"""Manual merge of heads 2244b5113efd and c1012aa6f30c

Revision ID: 8ea82bb18bfc
Revises: c1012aa6f30c
Create Date: 2024-08-08 04:14:58.542725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ea82bb18bfc'
down_revision: Union[str, None] = ('2244b5113efd', 'c1012aa6f30c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
