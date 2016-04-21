<%!
    from spline.format import format_date
    from spline_comic.views import FOLDER_PREVIEW_PAGE_COUNT
%>
<%inherit file="spline_comic:templates/_base.mako" />
<%namespace name="lib" file="spline_comic:templates/_lib.mako" />

<%block name="title">
Archive
</%block>

<%block name="header">
<h1>Archive</h1>
</%block>

<p class="gallery-archive-top-links">
    <a href="${request.route_url('comic.archive')}">Archive by folder</a> · Archive by date
</p>
<p class="gallery-archive-top-links">
    % for year in sorted(frozenset(item.date_published.year for item in items)):
        <a href="#archive-year-${year}">${year}</a>
        % if not loop.last:
            ·
        % endif
    % endfor
</p>

<section>
<table class="gallery-archive-by-date">
<col class="-month">
<col class="-folder">
<col class="-page">
<% group_alt = 2 %>
% for item, prev_item in zip(items, [None] + items):
    <%
        if prev_item is None:
            new_year = True
            new_month = True
            new_folder = True
        else:
            new_year = item.date_published.year != prev_item.date_published.year
            new_month = new_year or item.date_published.month != prev_item.date_published.month
            new_folder = item.folder != prev_item.folder

        if new_folder:
            group_alt = 3 - group_alt
    %>
    <tr class="-folder-group-${group_alt} ${'-new-month' if new_month else ''} ${'-new-year' if new_year else ''}"
    % if new_year:
        id="archive-year-${item.date_published.year}"
    % endif
    >
        % if new_month:
            <th class="-month">${item.date_published.strftime('%d %b %Y')}</th>
        % else:
            <td class="-month">${item.date_published.strftime('%d')}</td>
        % endif
        <th class="-folder">
            % if new_folder:
                <a href="${request.resource_url(item.folder)}">${item.folder.title}</a>
            % endif
        </th>
        <td class="-page">
            <a href="${request.resource_url(item)}">
                ${item.title or "page {}".format(item.page_number)}
            </a>
        </td>
    </tr>
% endfor
</table>
</section>
