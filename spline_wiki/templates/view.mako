<%!
    from spline.display.rendering import render_prose
%>
<%inherit file="/_base.mako" />

<%block name="title">${content.metadata.get('title', ['Untitled'])[-1]}</%block>

## TODO need a better list of wiki operations and whatevers here
## TODO parent?  breadcrumbs?
<p>
    <a href="${request.resource_url(request.context, '@@edit')}">edit</a>
    ·
    <a href="${request.resource_url(request.context, '@@history')}">history</a>
    ·
    translate??
    ·
    talk??
</p>

hello!  ${path} / ${request.view_name} / ${request.subpath}

<section>
${content}
</section>
