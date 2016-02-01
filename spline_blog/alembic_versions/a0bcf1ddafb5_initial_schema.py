"""Initial schema

Revision ID: a0bcf1ddafb5
Revises: None
Create Date: 2016-01-20 21:39:03.404948

"""

# revision identifiers, used by Alembic.
revision = 'a0bcf1ddafb5'
down_revision = None
branch_labels = ('blog',)

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('blog',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('title', sa.Unicode(), nullable=False),
        sa.Column('content', sa.UnicodeText(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_blog_timestamp'), 'blog', ['timestamp'], unique=False)
    op.alter_column('comic_pages', 'timezone',
               existing_type=sa.VARCHAR(),
               nullable=False)


def downgrade():
    op.alter_column('comic_pages', 'timezone',
        existing_type=sa.VARCHAR(),
        nullable=True)
    op.drop_index(op.f('ix_blog_timestamp'), table_name='blog')
    op.drop_table('blog')
