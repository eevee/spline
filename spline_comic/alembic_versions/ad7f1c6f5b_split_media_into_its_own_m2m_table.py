"""Split media into its own m2m table

Revision ID: ad7f1c6f5b
Revises: 534e3c50c8b
Create Date: 2015-06-29 20:59:34.396749

"""

# revision identifiers, used by Alembic.
revision = 'ad7f1c6f5b'
down_revision = '534e3c50c8b'
branch_labels = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'gallery_media',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('discriminator', sa.Enum('image', 'iframe', name='gallery_media__discriminator'), nullable=False),
        sa.Column('image_file', sa.Unicode(), nullable=True),
        sa.Column('thumbnail_file', sa.Unicode(), nullable=True),
        sa.Column('url', sa.Unicode(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    op.execute('''create sequence gallery_items_media_order_seq''')
    op.create_table(
        'gallery_items_media',
        sa.Column('gallery_item_id', sa.Integer(), nullable=False),
        sa.Column('gallery_media_id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False, server_default=sa.text("nextval('gallery_items_media_order_seq'::regclass)")),
        sa.ForeignKeyConstraint(['gallery_item_id'], ['comic_pages.id']),
        sa.ForeignKeyConstraint(['gallery_media_id'], ['gallery_media.id']),
        sa.PrimaryKeyConstraint('gallery_item_id', 'gallery_media_id'),
    )
    op.create_index(op.f('ix_gallery_items_media_order'), 'gallery_items_media', ['order'], unique=True)

    op.execute('''
        insert into gallery_media (discriminator, image_file, thumbnail_file)
        select 'image', file, file from comic_pages
    ''')
    op.execute('''
        insert into gallery_items_media (gallery_item_id, gallery_media_id)
        select comic_pages.id, gallery_media.id
        from comic_pages join gallery_media on gallery_media.image_file = comic_pages.file
    ''')

    op.drop_column('comic_pages', 'file')


def downgrade():
    op.add_column('comic_pages', sa.Column('file', sa.TEXT(), autoincrement=False, nullable=False, server_default=''))
    op.execute('''
        update comic_pages set file = (
            select image_file
            from gallery_items_media
            join gallery_media on gallery_items_media.gallery_media_id = gallery_media.id
            where gallery_items_media.gallery_item_id = comic_pages.id
            and gallery_media.discriminator = 'image'
            order by gallery_items_media."order" asc
            limit 1
        )
    ''')
    op.alter_column('comic_pages', 'file', server_default=None)

    op.drop_index(op.f('ix_gallery_items_media_order'), table_name='gallery_items_media')
    op.drop_table('gallery_items_media')
    op.drop_table('gallery_media')
    op.execute('''drop sequence gallery_items_media_order_seq''')
    op.execute('''drop type if exists gallery_media__discriminator''')
