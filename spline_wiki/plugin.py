from spline_wiki.models import Wiki


def includeme(config):
    """Pyramid's inclusion hook."""

    # TODO at startup:
    # - verify wiki is configured
    # - verify have write access to wiki dir
    # - verify wiki dir is a git repo?  fix if not?
    # - should the wiki dir itself be an object then?
    # hold up.  if those fail, should we die, or just let the plugin not load?

    wiki = Wiki(config.registry.settings['spline.wiki.root'])

    # Routing
    config.add_route('wiki', '/*traverse', factory=lambda request: wiki)

    config.scan('spline_wiki')
