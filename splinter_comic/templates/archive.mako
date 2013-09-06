<%!
    from splinter.format import format_date
%>
<%inherit file="splinter_comic:templates/_base.mako" />

<%block name="title">Archive for ${comic.title}</%block>
<%block name="subheader"><h2>Archive</h2></%block>

% if queue is not None:
## TODO admin-only indication
<section>
    <h1>Queue</h1>

    <p><a href="${request.route_url('comic.admin', comic)}" class="btn warning">Queue settings</a></p>

    <ul>
      % for page in queue:
        <li><a href="${request.route_url('comic.page', page)}">
            ${format_date(page.date_published)} ${page.title}
        </a></li>
      % endfor
    </ul>
</section>
% endif

<section>
    <h1>Archive</h1>

    <ul>
      % for page in pages:
        <li><a href="${request.route_url('comic.page', page)}">
            ${format_date(page.date_published)} ${page.title}
        </a></li>
      % endfor
    </ul>
</section>
