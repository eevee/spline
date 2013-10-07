from pyramid.response import Response
from pyramid.response import response_adapter
import zope.interface as zi


class Feed(object):
    def __init__(self, registry):
        self.registry = registry
        self.items = []

    def __iter__(self):
        for item in self.items:
            yield self.registry.getAdapter(item, IFeedItem)

    def populate_from_subscribers(self):
        self.registry.notify(self)

    def generate_atom(self):
        out = ''
        for item in self:
            out += str(item.timestamp) + "\n"

        return Response(out)


    # Subscriber API

    def add_feed_items(self, *items):
        self.items.extend(items)


class IFeedItem(zi.Interface):
    timestamp = zi.Attribute("timestamp")
    title = zi.Attribute("title")


@response_adapter(Feed)
def feed_to_response(feed):
    return feed.generate_atom()
