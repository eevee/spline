<%!
    from spline.display.rendering import render_prose
%>
<%inherit file="/_base.mako" />

<%block name="title">${content.metadata.get('title', ['Untitled'])[-1]}</%block>

## TODO need a better list of wiki operations and whatevers here
## TODO parent?  breadcrumbs?
<p>
    <a href="${request.resource_url(page, '@@edit')}">edit</a>
    ·
    <a href="${request.route_url(page, '@@history')}">history</a>
    ·
    translate??
    ·
    talk??
</p>

hello!  ${path} / ${request.view_name} / ${request.subpath}

<section>
${content}
</section>
