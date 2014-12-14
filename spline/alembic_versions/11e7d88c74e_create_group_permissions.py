"""create group permissions

Revision ID: 11e7d88c74e
Revises: None
Create Date: 2014-12-13 16:50:22.272172

"""

# revision identifiers, used by Alembic.
revision = '11e7d88c74e'
down_revision = 'cda6dcdb87'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('group_permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('scope', sa.Unicode(), nullable=True),
        sa.Column('permission', sa.Unicode(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('group_permissions')
