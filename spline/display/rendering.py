import bleach
import markdown
from markupsafe import Markup
from pyramid.renderers import get_renderer
import simplejson


def render_with_context(context, renderer_name, *args, **kwargs):
    renderer = get_renderer(renderer_name)

    template = renderer.template
    if renderer.defname:
        target = template.get_def(renderer.defname)
    else:
        target = template

    target.render_context(context, *args, **kwargs)
    return u''


def render_json(data):
    encoder = simplejson.JSONEncoderForHTML()
    return Markup(encoder.encode(data))


class RenderedMarkdown(Markup):
    def __new__(cls, base=u'', *args, **kwargs):
        metadata = kwargs.pop('metadata', {})
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
    return RenderedMarkdown(rendered, metadata=getattr(renderer, 'Meta', {}))


def render_html(html):
    # Idempotence
    if isinstance(html, Markup):
        return html

    return Markup(bleach.clean(
        html,
        tags=(
            'section',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'blockquote',
            'a', 'img',
            'abbr', 'acronym', 'code',
            'em', 'i', 'strong', 'b',
            'ul', 'ol', 'li',
            'hr', 'table', 'tr', 'td', 'th',
        ),
        attributes={
            '*': ['class'],
            'img': ['src', 'alt'],
        },
    ))
