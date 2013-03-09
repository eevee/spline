
def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('pastebin.list', '/')
    config.add_route('pastebin.view', '/{id:\d+}')
    config.add_route('pastebin.search', '/search')

    config.scan('splinter_pastebin')
