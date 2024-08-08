"""added replies table

Revision ID: 1df47466d698
Revises: 854472eb449d
Create Date: 2024-08-01 17:56:31.641943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1df47466d698'
down_revision: Union[str, None] = '69eb297622a4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    """
    op.create_table('replies',
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('comment_id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete="CASCADE"),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_replies_id'), 'replies', ['id'], unique=False)


def downgrade() -> None:
    """
    """
    op.drop_index(op.f('ix_replies_id'), table_name='replies')
    op.drop_table('replies')

