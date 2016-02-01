<%inherit file="/_base.mako" />
<%!
    import spline.format as libfmt
    from spline.display.rendering import render_html
%>

<%block name="title">${post.title}</%block>

<section>
    <header>
        <p><a href="${request.route_url('blog.index')}">Blog</a> »</p>
        <h1>
            ${post.title}
            <time class="unheader">${libfmt.format_datetime(post.timestamp)}</time>
        </h1>
    </header>
    <div>${render_html(post.content)}</div>
</section>
