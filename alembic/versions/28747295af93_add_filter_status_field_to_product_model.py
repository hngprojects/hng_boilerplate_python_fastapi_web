"""add filter_status field to Product model

Revision ID: 28747295af93
Revises: 5f9d01dc6cc9
Create Date: 2024-07-31 01:41:33.879947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28747295af93'
down_revision: Union[str, None] = '5f9d01dc6cc9'
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