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


class RenderedMarkdown(Markup):
    def __new__(cls, base=u'', *args, **kwargs):
        metadata = kwargs.pop('metadata', {})
        print(repr(args), repr(kwargs))
        self = super().__new__(cls, base, *args, **kwargs)
        self.metadata = metadata
        return self


def render_prose(prose):
    # Idempotence
    if isinstance(prose, Markup):
        return prose

    renderer = markdown.Markdown(
        extensions=['meta', 'def_list'],
        output_format='html5',
        safe_mode='escape',
    )
    rendered = renderer.convert(prose)

    # We trust the Markdown implementation to jettison any unexpected HTML.
    # Fingers crossed.
    return RenderedMarkdown(rendered, metadata=renderer.Meta)
