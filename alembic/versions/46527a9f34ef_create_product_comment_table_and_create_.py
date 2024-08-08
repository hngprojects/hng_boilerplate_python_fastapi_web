"""create product comment table and create relationship between products, product_comments in User model

Revision ID: 46527a9f34ef
Revises: 3b6d16e973a2
Create Date: 2024-08-08 00:26:47.226635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46527a9f34ef'
down_revision = '3b6d16e973a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if the table already exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'product_comments' not in inspector.get_table_names():
        op.create_table('product_comments',
        sa.Column('product_id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_product_comments_id'), 'product_comments', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_product_comments_id'), table_name='product_comments')
    op.drop_table('product_comments')
