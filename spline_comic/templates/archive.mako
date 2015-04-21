<%!
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">Archive for ${comic.title}</%block>

% for comic in comics:
<section>
    <%
        first_chapter_page = first_pages_by_comic[comic][0]
        # TODO what i actually want here is the /last/ page of the last chapter
        last_chapter_page = first_pages_by_comic[comic][-1]
    %>
    <h1 id="comic-${comic.title_slug}">
        ${comic.title}
        <span class="unheader">${format_date(first_chapter_page.local_date_published)} – ${format_date(last_chapter_page.local_date_published)}</span>
    </h1>

            <ul class="comic-page-grid">
            % for page in first_pages_by_comic[comic]:
                <li
                    % if page.is_queued:
                    class="privileged"
                    % endif
                >
                    <a href="${request.route_url('comic.page', page)}">
        <img src="${page.file.url_from_request(request)}"
            class="image-capped">
            </a>
                </li>
            % endfor
            </ul>
</section>
% endfor
