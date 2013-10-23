from pyramid.renderers import get_renderer

def render_with_context(context, renderer_name, *args, **kwargs):
    renderer = get_renderer(renderer_name)

    impl = renderer.implementation()
    if renderer.defname:
        target = impl.get_def(renderer.defname)
    else:
        target = impl

    target.render_context(context, *args, **kwargs)
    return u''
