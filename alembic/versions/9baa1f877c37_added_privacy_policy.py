"""added privacy policy

Revision ID: 9baa1f877c37
Revises: 5957c6e4194f
Create Date: 2024-08-06 13:55:57.804647

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9baa1f877c37'
down_revision: Union[str, None] = '5957c6e4194f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('privacy_policies',
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_privacy_policies_id'), 'privacy_policies', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_privacy_policies_id'), table_name='privacy_policies')
    op.drop_table('privacy_policies')
    # ### end Alembic commands ###
