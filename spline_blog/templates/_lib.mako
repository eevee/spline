<%!
    import spline.format as libfmt
    from spline.display.rendering import render_html
%>

<%def name="front_page_block(block)">
<section>
  % if block.last_post:
    <h1>
        <a href="${request.route_url('blog.view', post_id=block.last_post.id)}">${block.last_post.title}</a>
        <time class="unheader">${libfmt.format_datetime(block.last_post.timestamp)}</time>
    </h1>
    <div>${render_html(block.last_post.content)}</div>
  % else:
    no recent posts...
  % endif
</section>
</%def>
