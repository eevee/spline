"""Helpers for making nice pretty routes."""
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.properties import PropertyLoader

from splinter.models import session

import re


# nb: This is pretty conservative, only stripping out non-identifier-like
# ASCII.  It can be changed at any time, because slugs are (supposed to be...)
# stored alongside their respective titles, and so this function is only called
# when a title is first assigned.
SLUG_RE = re.compile(ur'[^a-zA-Z0-9]+')
def to_slug(title):
    """Given a page (or whatever) title, return a URL-friendly slug."""
    slug = (
        SLUG_RE.sub(u'-', title)
        .strip(u'-')
        .lower()
    )

    if not slug:
        # Hmm.
        slug = u'tsilb'

    return slug


def _guess_relationship(child, parent):
    """Given two mapped classes, return a wild guess at a relationship that
    leads from the child to the parent.

    The logic is the same as that used in Query.with_parent, albeit backwards.
    """
    child_mapper = class_mapper(child)
    parent_mapper = class_mapper(parent)

    for prop in child_mapper.iterate_properties:
        if isinstance(prop, PropertyLoader) and prop.mapper is parent_mapper:
            return prop

    raise InvalidRequestError(
        "Can't find a relationship from {0} to {1}"
        .format(child.__name__, parent.__name__))


# TODO maybe grab the config object and do the adding itself, so the caller
# code is a little less repetitive and ugly
# TODO i would still like deriving to work with `with`
# TODO this should probably just accept a prefix ('/foos/{foo_id}') since
# that's almost universally how it will be used
class DatabaseRouteConnector(object):
    """Happy mapping between Pyramid routing and SQLA schemata.

    Use as follows:

        drc = DatabaseRouteConnector('foo_id', FooTable.id)
        config.add_route('foo_view', '/foos/{foo_id}', **drc.kwargs)

    Now your view function will be passed a ``FooTable`` object as its
    ``context`` argument.  Magic!

    Generating URLs works the same way:

        request.route_url('foo_view', foo_object)
    """

    def __init__(self, marker, column, slug=None, parent=None, relchain=None):
        self.marker = marker
        self.column = column
        self.slug_column = slug

        assert bool(parent) == bool(relchain)
        self.parent = parent
        self.relchain = relchain

    @property
    def table(self):
        return self.column.class_

    @property
    def kwargs(self):
        return dict(
            pregenerator=self.pregenerator,
            factory=self.root_factory,
        )

    def derive(self, marker, column, slug=None, relchain=None):
        """Derive a new connector that chains to this one.  Use for
        hierarchical URLs, where both a parent object and some child object
        exist in the route.
        """
        if not relchain:
            relchain = (_guess_relationship(column.class_, self.table),)

        return type(self)(
            marker,
            column,
            slug=slug,
            parent=self,
            relchain=relchain)

    def pregenerator(self, request, elements, kw):
        """Turn an ORM object passed positionally to route_url into the
        appropriate set of keywords for building a URL.
        """
        if not elements or not isinstance(elements[0], self.table):
            if elements:
                got = repr(elements[0])
            else:
                got = "nothing"

            raise TypeError(
                "Please pass a {0} instance to route_url; got {1}"
                .format(self.table.__name__, got))

        row = elements[0]
        kw[self.marker] = self.column.__get__(row, type(row))

        relchain = ()
        current = self
        while current:
            for rel in relchain:
                row = rel.__get__(row, type(row))

            # Append the slug, if any
            ident = unicode(current.column.__get__(row, type(row)))
            if current.slug_column:
                slug = unicode(current.slug_column.__get__(row, type(row)))
                if slug:
                    ident += u'-' + slug
            kw[current.marker] = ident

            relchain = current.relchain
            current = current.parent

        return elements[1:], kw

    def root_factory(self, request):
        """Given a request with a matched URL, produce the object referred to
        by that URL.

        Raise a 404 if no such object exists.
        """
        table = self.column.class_
        query = session.query(table)

        relchain = ()
        current = self
        while current:
            for rel in relchain:
                query = query.join(rel)

            if current.marker in request.matchdict:
                ident = request.matchdict[current.marker]
                if current.slug_column:
                    # Split the "real" identifier from the slug
                    ident, _, _ = ident.partition(u'-')
                    # TODO redirect if any slug doesn't match the db
                    # TODO come to think of it...  contains_eager?

                query = query.filter(current.column == ident)
            elif current is self:
                # Missing the identifier for the most specific model, which...
                # don't make sense
                raise HTTPNotFound()

            relchain = current.relchain
            current = current.parent

        try:
            row = query.one()
        except NoResultFound:
            # Note that MultipleResultsFound isn't caught, because that should
            # not be *possible* and indicates a programming error
            raise HTTPNotFound()

        return row
