"""added region, timezone and language table

Revision ID: eb6fe394d75b
Revises: 70dab65f6844
Create Date: 2024-08-01 02:13:34.310685

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb6fe394d75b'
down_revision: Union[str, None] = '085de908c797'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('regions',
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('region', sa.String(), nullable=False),
    sa.Column('language', sa.String(), nullable=True),
    sa.Column('timezone', sa.String(), nullable=True),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_regions_id'), 'regions', ['id'], unique=False)
    op.add_column('contact_us', sa.Column('org_id', sa.String(), nullable=False))
    op.create_foreign_key(None, 'contact_us', 'organizations', ['org_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'contact_us', type_='foreignkey')
    op.drop_column('contact_us', 'org_id')
    op.drop_index(op.f('ix_regions_id'), table_name='regions')
    op.drop_table('regions')
    # ### end Alembic commands ###
