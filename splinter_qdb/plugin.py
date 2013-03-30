def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('qdb.list', '/')

    config.scan('splinter_qdb')
