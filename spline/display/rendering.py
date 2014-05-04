import markdown
from markupsafe import Markup
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


def render_prose(prose):
    rendered = markdown.markdown(
        prose,
        extensions=[],
        output_format='html5',
        safe_mode='escape',
    )

    # We trust the Markdown implementation.  Fingers crossed.
    return Markup(rendered)
