"""Use nested set for gallery folders

Revision ID: 497817c8e37
Revises: 3fd511a94b4
Create Date: 2015-05-30 16:58:18.350497

"""

# revision identifiers, used by Alembic.
revision = '497817c8e37'
down_revision = '58c21256267'
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('comic_chapters', sa.Column('left', sa.Integer(), nullable=True))
    op.add_column('comic_chapters', sa.Column('right', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'comic_chapters', ['right'], deferrable=True, initially='DEFERRED')
    op.create_unique_constraint(None, 'comic_chapters', ['left'], deferrable=True, initially='DEFERRED')
    op.execute('''
        with numbers as (select id, row_number() over (order by id) as num from comic_chapters)
        update comic_chapters
        set "left" = (select num from numbers where numbers.id = comic_chapters.id) * 2 - 1,
        "right" = (select num from numbers where numbers.id = comic_chapters.id) * 2
    ''')
    op.alter_column('comic_chapters', 'left', existing_type=sa.Integer(), nullable=False)
    op.alter_column('comic_chapters', 'right', existing_type=sa.Integer(), nullable=False)


def downgrade():
    op.drop_column('comic_chapters', 'right')
    op.drop_column('comic_chapters', 'left')
