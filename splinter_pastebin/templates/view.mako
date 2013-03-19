<%inherit file="/_base.mako"/>

<%block name="title">viewing: ${paste.nice_title}</%block>

<section>
    <h2>${paste.nice_title}</h2>
    <% import pygments.formatters %>
    <style>${pygments.formatters.HtmlFormatter().get_style_defs('.highlight')}</style>

    ${pretty_content | n}

    <p>brought to you by ${paste.nice_author}</p>
</section>
