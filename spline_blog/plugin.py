from collections import namedtuple

from pyramid.events import subscriber

from spline.events import FrontPageActivity
from spline.events import FrontPageLayout
from spline.models import session
from spline_blog.models import BlogPost
# TODO lol.  lolll
from spline_comic.plugin import Plugin


FrontPageBlock = namedtuple('FrontPageBlock', [
    'renderer',
    'last_post',
])


# TODO maybe an activity too?
@subscriber(FrontPageLayout)
def offer_blocks(event):
    last_post = session.query(BlogPost).order_by(BlogPost.timestamp.desc()).first()

    block = FrontPageBlock(
        renderer='spline_blog:templates/_lib#front_page_block.mako',
        last_post=last_post,
    )
    event.blocks.append(block)


blog_plugin = Plugin('blog', __name__)

# TODO honestly this seems like something that /could/ be merged with comics,
# if you were clever about it.  then you'd have something like tumblr.

@blog_plugin.configurator
def configure_blog(self, config):
    config.register_spline_plugin(self)

    # TODO same stupid hack as for comic
    class DumbPermissionHack:
        __scope__ = 'blog'

        def __init__(self, request):
            pass

    # Routing
    config.add_route('blog.index', '/', factory=DumbPermissionHack)
    config.add_route('blog.new', '/@@new/', factory=DumbPermissionHack)
    config.add_route('blog.ckupload', '/@@ckeditor-upload/', factory=DumbPermissionHack)
    # TODO this wants a resource, but atm it still needs doing manually, and eh
    config.add_route('blog.view', '{post_id:\d+}/')

    config.scan('spline_blog')
