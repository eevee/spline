<%!
    from spline.display.rendering import render_prose
%>
<%inherit file="/_base.mako" />

hello!  ${path} / ${request.view_name} / ${request.subpath}

<section>
${render_prose(content)}
</section>
