"""Add timezone to comic_pages

Revision ID: 14aa3a09a90
Revises: 1dea06bc811
Create Date: 2015-02-06 00:12:02.452795

"""

# revision identifiers, used by Alembic.
revision = '14aa3a09a90'
down_revision = '1dea06bc811'
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('comic_pages', sa.Column('timezone', sa.Unicode()))

    # populate the column based on the comic's timezone (the best we've got)
    # i'd have to copy all the table defs here to do this with core or orm so
    # fuck it
    op.execute("""
        update comic_pages set timezone = (
            select comics.config_timezone from comic_chapters
            join comics on comic_chapters.comic_id = comics.id
            where comic_chapters.id = comic_pages.chapter_id
        )
    """)

    # now add the NOT NULL constraint
    op.alter_column('comic_pages', 'timezone', server_default=None)


def downgrade():
    op.drop_column('comic_pages', 'timezone')
