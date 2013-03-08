

def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('paste', '/')
    config.add_route('view', '/{id:\d+}')
    config.add_route('search', '/search')

    config.scan('splinter_pastebin')
