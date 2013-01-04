from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    )



@view_config(route_name='home', renderer='/index.mako')
def index(request):
    return {}
