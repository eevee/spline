from pyramid.httpexceptions import HTTPSeeOther
from pyramid.view import view_config

from spline.models import Group, GroupPermission, session


# TODO this should really, really be in the plugins themselves.
# but even plugin definition is kind of up in the air.
# and i'm still iffy on the 'scope' thing, which for example doesn't seem to be
# working so hot for comic administration where there /is/ no scope.
# also i never figured out how to add special things like "owner only" or
# scoped to specific objects like subforums
ALL_KNOWN_PERMISSIONS_XXX = dict(
    wiki=['edit', 'propose'],
    comic=['admin', 'queue'],
)


# TODO this page isn't very pretty, oh well
# TODO no way to add or remove groups
# TODO or see who's in them (or browse users at all)
# TODO no "normal" group or "guest" group
# TODO no group inheritance
@view_config(
    route_name='__core__.admin.permissions',
    request_method='GET',
    renderer='/admin/permissions.mako')
def permissions(request):
    perms = session.query(GroupPermission).all()
    groups = session.query(Group).all()

    all_privileges = []
    for scope, priv_names in sorted(ALL_KNOWN_PERMISSIONS_XXX.items()):
        for priv_name in priv_names:
            all_privileges.append((scope, priv_name))

    return dict(
        permissions=perms,
        groups=groups,
        all_privileges=all_privileges,
    )


@view_config(
    route_name='__core__.admin.permissions.grant',
    request_method='POST')
def permissions_grant(request):
    # TODO error checking, eh.  is there even a flash thing yet, haha
    data = dict(
        group_id=request.POST['group'],
        scope=request.POST['scope'],
        permission=request.POST['priv'],
    )

    existing = session.query(GroupPermission).filter_by(**data).all()

    if not existing:
        session.add(GroupPermission(**data))

    return HTTPSeeOther(location=request.route_url('__core__.admin.permissions'))


@view_config(
    route_name='__core__.admin.permissions.revoke',
    request_method='POST')
def permissions_revoke(request):
    # TODO error checking, eh.  is there even a flash thing yet, haha
    data = dict(
        group_id=request.POST['group'],
        scope=request.POST['scope'],
        permission=request.POST['priv'],
    )

    session.query(GroupPermission).filter_by(**data).delete()

    return HTTPSeeOther(location=request.route_url('__core__.admin.permissions'))
