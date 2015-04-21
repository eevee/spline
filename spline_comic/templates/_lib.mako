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
<section>
    <h1>
        ${block.latest_page.comic.title} comic
    </h1>
    <div class="block-body media">
        <img src="${block.chapter_cover_page.file.url_from_request(request)}"
            class="media-inset image-capped">

        <div class="media-body media-body--with-footer">
            <div class="media-body-main">
                <%
                    page = block.latest_page
                    chapter = page.chapter
                %>
                <p>
                    Latest page, posted
                    ${libformat.format_relative_date(page.date_published)}:
                    <br>
                    <a href="${request.route_url('comic.page', page)}">
                        ${chapter.title}, page ${page.page_number}
                        % if page.title:
                            — “${page.title}”
                        % endif
                    </a>
                </p>
            </div>

            <div class="media-body-footer">
                <ul class="inline-list">
                    <li><a href="${request.route_url('comic.page', block.comic_first_page)}">Start of the entire comic</li>
                    <li><a href="${request.route_url('comic.page', block.chapter_cover_page)}">Start of this chapter</a></li>
                    <li><a href="${request.route_url('comic.archive')}">Archive</a></li>
                </ul>
            </div>
        </div>
    </div>
</section>
</%def>
