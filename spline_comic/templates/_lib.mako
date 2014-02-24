<%namespace name="libcore" file="spline:templates/_lib.mako" />
<%! import spline.format as libformat %>

<%def name="render_activity(page)">
<div class="-header">
    <div class="-timestamp">${libcore.timestamp(page.date_published)}</div>
    <div class="-title">
        <a href="${request.route_url('comic.page', page)}">${page.title or u'untitled'}</a>
    </div>
    <div class="-user-etc">
        new comic page for ${page.comic.title}
        <br>
        posted by ${libcore.user(page.author)}
    </div>
</div>
</%def>

<%def name="front_page_block(block)">
<section class="block">
    <header>
        ${block.latest_page.comic.title}
    </header>
    <div class="block-body media">
        <img src="${block.chapter_cover_page.file.url_from_request(request)}"
            class="media-inset image-capped">

        <div class="media-body">
            <%
                page = block.latest_page
                chapter = page.chapter
            %>
            <p>
                Posted ${libformat.format_date(page.date_published)}:
                <a href="${request.route_url('comic.page', page)}">
                    “${chapter.title}”, page ${page.page_number}
                    % if page.title:
                        (${page.title})
                    % endif
                </a>
            </p>

            <ul>
                <li><a href="${request.route_url('comic.page', block.chapter_cover_page)}">Read this chapter from the beginning</a></li>
                <li><a href="${request.route_url('comic.archive', page.comic)}#chapter-${chapter.title_slug}">Browse this chapter in the archive</a></li>
                <li><a href="${request.route_url('comic.page', block.comic_first_page)}">Read the entire comic from the beginning</li>
                <li><a href="${request.route_url('comic.archive', page.comic)}">Browse the entire archive</a></li>
            </ul>
        </div>
    </div>
</section>
</%def>
