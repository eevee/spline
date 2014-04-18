from pyramid.renderers import get_renderer

def render_with_context(context, renderer_name, *args, **kwargs):
    renderer = get_renderer(renderer_name)

    template = renderer.template
    if renderer.defname:
        target = template.get_def(renderer.defname)
    else:
        target = template

    target.render_context(context, *args, **kwargs)
    return u''
