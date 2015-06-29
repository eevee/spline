"""Create a view for folder parentage

Revision ID: 534e3c50c8b
Revises: 497817c8e37
Create Date: 2015-06-28 18:06:05.163657

"""

# revision identifiers, used by Alembic.
revision = '534e3c50c8b'
down_revision = '497817c8e37'
branch_labels = None

from alembic import op


def upgrade():
    op.execute('''
        CREATE VIEW gallery_folder__parent AS
        SELECT DISTINCT ON (comic_chapters_1.id)
            comic_chapters_1.id AS child_id,
            comic_chapters_2.id AS parent_id
        FROM comic_chapters AS comic_chapters_1
        JOIN comic_chapters AS comic_chapters_2
            ON comic_chapters_2."left" < comic_chapters_1."left"
            AND comic_chapters_1."right" < comic_chapters_2."right"
        ORDER BY comic_chapters_1.id, comic_chapters_2."left"
    ''')


def downgrade():
    op.execute('''DROP VIEW gallery_folder__parent''')
