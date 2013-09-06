<%!
    from splinter.format import format_date
%>
<%inherit file="splinter_comic:templates/_base.mako" />

<%block name="title">Archive for ${comic.title}</%block>
<%block name="subheader"><h2>Archive</h2></%block>

<section>
    <ul>
      % for page in pages:
        <li><a href="${request.route_url('comic.page', page)}">
            ${format_date(page.timestamp)} ${page.title}
        </a></li>
      % endfor
    </ul>

</section>
