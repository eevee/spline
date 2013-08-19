<%!
    from splinter.format import format_date
%>
<%inherit file="splinter:templates/_base.mako" />

<section>
    <h1>Archive</h1>

    <ul>
      % for page in pages:
        <li><a href="${request.route_url('comic.page', id=page.id)}">
            ${format_date(page.timestamp)} ${page.title}
        </a></li>
      % endfor
    </ul>

</section>
