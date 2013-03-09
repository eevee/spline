
def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('love.list', '/')
    config.add_route('love.express', '/express')

    config.scan('splinter_love')
