def includeme(config):
    """Pyramid's inclusion hook."""

    # Routing
    config.add_route('qdb.list', '/')
    config.add_route('qdb.view', '/{id:\d+}')

    config.scan('splinter_qdb')
