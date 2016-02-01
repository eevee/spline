<%inherit file="/_base.mako" />
<%namespace file="spline:templates/_lib.mako" name="lib" />
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

## TODO ok i guess this shouldn't be specific to spline_gallery...  (really it
## should be specific to a disqus plugin)
% if 'spline_gallery.disqus' in request.registry.settings:
<section class="comments">
    <h1>Comments</h1>
    ${lib.disqus(
        request.registry.settings['spline_gallery.disqus'],
        request.route_url('blog.view', post_id=post.id),
        post.title,
    )}
</section>
% endif
