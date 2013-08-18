def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('comic.index', '/')

    config.scan('splinter_comic')
