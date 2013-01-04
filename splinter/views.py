from pyramid.response import Response
from pyramid.view import view_config

from .models import session


@view_config(route_name='home', renderer='/index.mako')
def index(request):
    return {}
