<%!
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">Archive for ${comic.title}</%block>
<%block name="subheader"><h2>Archive</h2></%block>

    ##<p><a href="${request.route_url('comic.admin', comic)}" class="btn warning">Queue settings</a></p>
## TODO admin-only indication for queued pages?
% for chapter in chapters:
<section>
    <%
        first_page = pages_by_chapter[chapter][0]
        last_page = pages_by_chapter[chapter][-1]
    %>
    <h1 id="chapter-${chapter.title_slug}">
        ${chapter.title}
        <span class="unheader">${format_date(first_page.date_published)} – ${format_date(last_page.date_published)}</span>
    </h1>

    <div class="media">
        <img src="${request.static_url('spline:../data/filestore/' + first_page.file)}"
            class="media-inset image-capped">

        <div class="media-body">
            <ul class="comic-page-grid">
            % for page in pages_by_chapter[chapter]:
                <li
                    % if page.is_queued:
                    class="privileged"
                    % endif
                >
                    <a href="${request.route_url('comic.page', page)}">
                        ${page.page_number}</a>
                </li>
            % endfor
            </ul>
        </div>
    </div>
</section>
% endfor
