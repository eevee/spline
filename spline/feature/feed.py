from operator import attrgetter

from lxml import etree
from lxml.builder import ElementMaker
from pyramid.response import Response
from pyramid.response import response_adapter
import zope.interface as zi

ATOM_NS = 'http://www.w3.org/2005/Atom'
atom_el = ElementMaker(namespace=ATOM_NS, nsmap={None: ATOM_NS})


# TODO documentation!
class Feed(object):
    def __init__(self, request, title):
        self._raw_items = []

        self.request = request
        self.title = title

    def items(self):
        feed_items = []
        for item in self._raw_items:
            feed_items.append(
                self.request.registry.getAdapter(item, IFeedItem))

        feed_items.sort(key=attrgetter('timestamp'), reverse=True)

        return feed_items

    def populate_from_subscribers(self):
        self.request.registry.notify(self)

    def generate_atom(self):
        items = self.items()

        # TODO path_qs may not be right if the endpoint takes args (for some
        # reason)...  maybe overrideable?
        feed_url = self.request.application_url + self.request.path_qs

        # TODO: mark the document with an xml:lang
        root = atom_el.feed(
            # Required
            atom_el.id(feed_url),
            atom_el.title(self.title),
            atom_el.updated(items[0].timestamp.isoformat()),

            # Recommended
            #atom_el.author("..."),
            atom_el.link(rel="self", href=feed_url),

            # Optional
            #atom_el.category("..."),
            #atom_el.contributor("..."),
            #atom_el.generator("..."),
            #atom_el.icon("..."),
            #atom_el.logo("..."),
            #atom_el.rights("..."),
            #atom_el.subtitle("..."),
        )

        for item in items:
            url = item.generate_url(self.request)
            root.append(atom_el.entry(
                # Required
                atom_el.id(url),
                atom_el.title(item.title),
                atom_el.updated(item.timestamp.isoformat()),

                # Recommended
                # TODO author is REQUIRED if the whole feed lacks one!
                #atom_el.author("TODO"),
                #atom_el.content("TODO"),
                atom_el.link(rel="alternate", href=url),
                #atom_el.summary("TODO"),

                # Optional
                #atom_el.category("..."),
                #atom_el.contributor("..."),
                #atom_el.published("..."),
                #atom_el.source("..."),
                #atom_el.rights("..."),
            ))

        xml = etree.tostring(
            root,
            pretty_print=True,
            encoding="UTF-8",
            xml_declaration=True)
        return Response(xml, content_type="text/xml", charset="UTF-8")


    # Subscriber API

    def add_feed_items(self, *items):
        self._raw_items.extend(items)


class IFeedItem(zi.Interface):
    timestamp = zi.Attribute("timestamp")
    title = zi.Attribute("title")

    # TODO it would be super cool if this would default to resource_url (and
    # that actually worked!)
    def generate_url(self, request):
        """Return a URL to this item."""


@response_adapter(Feed)
def feed_to_response(feed):
    return feed.generate_atom()
