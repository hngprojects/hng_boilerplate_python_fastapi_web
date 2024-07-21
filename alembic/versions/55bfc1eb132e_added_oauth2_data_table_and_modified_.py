"""add oauth2_data table, and modify users.password field to nullable


Revision ID: 55bfc1eb132e
Revises: 534047ee3520
Create Date: 2024-07-21 22:41:01.780256


"""
from typing import Sequence, Union


from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '55bfc1eb132e'
down_revision: Union[str, None] = '534047ee3520'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the oauth2_data table
    op.create_table(
        'oauth2_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=sa.text('uuid_generate_v7()')),
        sa.Column('oauth2_provider', sa.String(length=60), nullable=False),
        sa.Column('sub', sa.String(length=60), nullable=False),
        sa.Column('access_token', sa.String(length=255), nullable=False),
        sa.Column('refresh_token', sa.String(length=255), nullable=True),
        sa.Column('id_token', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )


    # Modify the users table
    op.alter_column(
        'users',
        'password',
        existing_type=sa.String(length=255),
        nullable=True
    )


    # Add foreign key column to the users table for oauth2_data
    op.add_column(
        'users',
        sa.Column('oauth2_data_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('oauth2_data.id', ondelete='SET NULL'), nullable=True)
    )


def downgrade() -> None:
    # Drop the oauth2_data table
    op.drop_table('oauth2_data')


    # Remove foreign key column from the users table
    op.drop_column('users', 'oauth2_data_id')


    # Revert the users table column change
    op.alter_column(
        'users',
        'password',
        existing_type=sa.String(length=255),
        nullable=False
    )
