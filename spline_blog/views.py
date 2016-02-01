from io import BytesIO
import os.path
import subprocess

from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound

from spline.models import session
from spline_blog.models import BlogPost
# TODO TODO YIKES TODO TODO
from spline_comic.models import GalleryMedia_Image


@view_config(
    route_name='blog.index',
    request_method='GET',
    renderer='spline_blog:templates/index.mako')
def index(request):
    blog_posts = session.query(BlogPost)

    return dict(
        blog_posts=blog_posts,
    )


@view_config(
    route_name='blog.view',
    request_method='GET',
    renderer='spline_blog:templates/view.mako')
def view(request):
    try:
        post = session.query(BlogPost).filter_by(id=request.matchdict['post_id']).one()
    except NoResultFound:
        return HTTPNotFound

    return dict(
        post=post,
    )


@view_config(
    route_name='blog.new',
    permission='post',
    request_method='GET',
    renderer='spline_blog:templates/new.mako')
def new(request):
    return dict()


@view_config(
    route_name='blog.new',
    permission='post',
    request_method='POST')
def new__post(request):
    post = BlogPost(
        title=request.POST['title'],
        content=request.POST['content'],
    )
    session.add(post)
    session.flush()

    return HTTPSeeOther(location=request.route_url('blog.index'))


@view_config(
    route_name='blog.ckupload',
    permission='post',
    request_method='POST',
    renderer='json')
def ckeditor_upload(request):
    # TODO is there anything to validate here
    # TODO this is exactly duplicated from spline_comic's uploading and could
    # stand to be part of filestore or something?
    file_upload = request.POST['upload']
    fh = file_upload.file

    from spline.feature.filestore import IStorage
    storage = request.registry.queryUtility(IStorage)

    _, ext = os.path.splitext(file_upload.filename)
    filename = storage.store(fh, ext)
    # TODO ha ha this is stupid
    # TODO very skinny images shouldn't be blindly made 200x200
    fh.seek(0)
    thumb = subprocess.check_output(['convert', '-', '-resize', '200x200', '-'], stdin=fh)
    # TODO this interface is bad also
    # TODO do i actually need a thumbnail for this?  might as well i guess
    thumbname = storage.store(BytesIO(thumb), ext)
    # TODO wire into transaction so the file gets deleted on rollback

    media = GalleryMedia_Image(
        image_file=os.path.basename(filename),
        thumbnail_file=os.path.basename(thumbname),
    )
    # TODO i want SQLA to automatically do the column type's cast in the ORM
    # constructor, but i don't know how.  i think i had this same problem in
    # yelp code too.
    from spline.feature.filestore import FileReference
    image_file = FileReference(media.image_file)

    # TODO return error dict on...  error
    return dict(
        uploaded=1,
        fileName=filename,
        url=image_file.url_from_request(request),
    )
