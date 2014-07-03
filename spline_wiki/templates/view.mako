<%!
    from spline.display.rendering import render_prose
%>
<%inherit file="/_base.mako" />

<%block name="title">${content.metadata.get('title', ['Untitled'])[-1]}</%block>

## TODO need a better list of wiki operations and whatevers here
## TODO parent?  breadcrumbs?
<p>
    <a href="${request.route_url('wiki', '@@edit', traverse=path)}">edit</a>
    ·
    <a href="${request.route_url('wiki', '@@history', traverse=path)}">history</a>
    ·
    translate??
    ·
    talk??
</p>

hello!  ${path} / ${request.view_name} / ${request.subpath}

<section>
${content}
</section>
