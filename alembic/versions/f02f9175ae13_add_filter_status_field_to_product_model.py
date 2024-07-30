"""add filter_status field to Product model

Revision ID: f02f9175ae13
Revises: d0fdcf651c1c
Create Date: 2024-07-30 21:50:33.043677

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f02f9175ae13'
down_revision: Union[str, None] = 'd0fdcf651c1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type
    op.execute("""
        CREATE TYPE productfilterstatusenum AS ENUM ('published', 'draft')
    """)

    # Add the column using the enum type
    op.add_column('products', sa.Column('filter_status', sa.Enum('published', 'draft', name='productfilterstatusenum'), nullable=True))


def downgrade() -> None:
    # Drop the column
    op.drop_column('products', 'filter_status')

    # Drop the enum type
    op.execute("DROP TYPE productfilterstatusenum")
