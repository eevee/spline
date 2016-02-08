<%!
    import spline.format as libfmt
    from spline.display.rendering import render_html
    from spline.display.rendering import trim_html
%>

<%def name="front_page_block(block)">
<section>
  % if block.last_post:
    <h1>
        <a href="${request.route_url('blog.view', post_id=block.last_post.id)}">
          % if block.last_post.title:
            ${block.last_post.title}
          % else:
            <em>untitled</em>
          % endif
        </a>
        <time class="unheader">${libfmt.format_datetime(block.last_post.timestamp)}</time>
    </h1>
    <div class="prose">${trim_html(render_html(block.last_post.content))}</div>
    <p><a href="${request.route_url('blog.view', post_id=block.last_post.id)}">Keep reading</a></p>
  % else:
    no recent posts...
  % endif
</section>
</%def>
