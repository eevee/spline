from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config

from spline.models import User, session
from spline_love.models import Love


# TODO: permission=Authenticated?  on both of these
@view_config(route_name='love.express', request_method='GET', renderer='spline_love:templates/express.mako')
def express_love(request):
    return dict()

@view_config(route_name='love.express', request_method='POST')
def express_love__do(request):
    # TODO real form handling thx

    source = request.user
    # TODO error handling lol
    target = session.query(User).filter_by(name=request.POST['target']).one()

    session.add(Love(
        source=source,
        target=target,
        comment=request.POST['comment'],
    ))

    return HTTPSeeOther(request.route_url('love.list'))


@view_config(route_name='love.list', request_method='GET', renderer='spline_love:templates/list.mako')
def list_love(request):
    loves = session.query(Love).order_by(Love.timestamp.desc())
    return dict(
        loves=loves,
    )

