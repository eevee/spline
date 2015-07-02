"""Database-backed authentication and authorization policies for Pyramid."""

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IAuthorizationPolicy
from zope.interface import implementer

from spline.models import User
from spline.models import session


@implementer(IAuthorizationPolicy)
class RoleAuthorizationPolicy:
    def permits(self, context, principals, permission):
        scope = context.__scope__
        return any(principal.can(scope, permission) for principal in principals)

    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError


@implementer(IAuthenticationPolicy)
class DatabaseAuthenticationPolicy:
    userid_key = '__core__.auth.userid'

    def authenticated_userid(self, request):
        userid = self.unauthenticated_userid(request)
        if userid:
            return session.query(User).get(userid)
        else:
            return None

    def effective_principals(self, request):
        if request.user:
            return [request.user]
        else:
            return []

    def remember(self, request, principal, **kw):
        request.session[self.userid_key] = principal.id
        return []

    def forget(self, request):
        if self.userid_key in request.session:
            del request.session[self.userid_key]
        return []

    def unauthenticated_userid(self, request):
        return request.session.get(self.userid_key)
