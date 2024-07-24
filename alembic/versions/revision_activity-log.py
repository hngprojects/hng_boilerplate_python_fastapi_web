"""add activity logs table

Create Date: 2024-07-23

"""
from alembic import op
import sqlalchemy as sa

revision = ''
down_revision = ''
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'activity_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now(), nullable=False)
    )

def downgrade():
    op.drop_table('activity_logs')
