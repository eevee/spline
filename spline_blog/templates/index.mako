<%inherit file="/_base.mako" />
<%!
    import spline.format as libfmt
%>

<header>
    <h1>Blog</h1>
</header>
% for post in blog_posts:
<p>
    <a href="${request.route_url('blog.view', post_id=post.id)}">${post.title}</a>
    — ${libfmt.format_datetime(post.timestamp)}
</p>
% endfor
