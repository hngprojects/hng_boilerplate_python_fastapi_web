"""added Rate Limits table

Revision ID: 2d0f5c131dba
Revises: eca40a718b7a
Create Date: 2024-07-24 23:25:59.269937

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d0f5c131dba'
down_revision: Union[str, None] = 'eca40a718b7a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # create Rate Limiting Table
    op.create_table('rate_limits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('client_ip', sa.String(), nullable=False),
        sa.Column('count', sa.Integer, nullable=False, server_default='0'),
        sa.Column('start_time', sa.Float, nullable=False, ),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # drop the rate limit table
    op.drop_table('rate_limits')
