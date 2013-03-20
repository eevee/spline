<%inherit file="/_base.mako"/>

<%block name="title">paste: ${paste.nice_title}</%block>

<%! import pygments.formatters %>
<style>${pygments.formatters.HtmlFormatter().get_style_defs('.highlight')}</style>

<section>
    <h1>${paste.nice_title}</h1>
    <p>Pasted by ${paste.nice_author} on ${paste.timestamp}</p>
    <p>
        % if paste.syntax:
        Formatted as ${paste.syntax}
        % else:
        Unformatted
        % endif
        · ${paste.lines} lines, ${paste.size} bytes
    </p>

    ${pretty_content | n}
</section>
