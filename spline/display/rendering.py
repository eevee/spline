from collections import deque

import bleach
import html5lib
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
            'p', 'blockquote', 'br', 'hr',
            'a', 'img',
            'abbr', 'acronym', 'code',
            'em', 'i', 'strong', 'b',
            'ul', 'ol', 'li',
            'hr', 'table', 'tr', 'td', 'th',
        ),
        attributes={
            '*': ['class'],
            'a': ['href'],
            'img': ['src', 'alt'],
        },
    ))


class TrimFilter:
    def __init__(self, source):
        self.source = source

    def __getattr__(self, name):
        return getattr(self.source, name)

    def __iter__(self):
        limit = 400

        text_seen = 0
        token_stack = deque()
        for token in self.source:
            if token['type'] == 'StartTag':
                token_stack.append(token)
            elif token['type'] == 'EndTag':
                token_stack.pop()
            elif token['type'] == 'Characters':
                text_seen += len(token['data'])
                if text_seen > limit and token_stack[-1]['name'] in (
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'blockquote',
                        'br', 'hr', 'p', 'li', 'td', 'th'):
                    yield token
                    yield dict(token, data=' …')
                    while token_stack:
                        yield dict(token_stack.pop(), **{'type': 'StartTag'})
                    return

            yield token


def trim_html(html):
    if not isinstance(html, Markup):
        raise TypeError("trim_html: expected Markup, got {!r}".format(type(html)))

    # TODO i think this could be combined with the bleach.clean call to avoid a
    # double parse?  filters apply during serialization, bleach applies during
    # tokenization
    # TODO alternatively, could this apply during tokenization to avoid
    # bothering with any markup we're not even going to show?
    tree = html5lib.parse(html)
    walker = html5lib.getTreeWalker('etree')
    stream = walker(tree)
    stream = TrimFilter(stream)
    serializer = html5lib.serializer.HTMLSerializer()

    return Markup(u''.join(serializer.serialize(stream)).strip())
