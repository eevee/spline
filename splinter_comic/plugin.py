def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('comic.most-recent', '/')
    config.add_route('comic.page', '/page/{id:\d+}/')

    config.scan('splinter_comic')
