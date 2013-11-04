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
        <img src="${request.static_url('spline:../data/filestore/' + block.chapter_cover_page.file)}"
            class="media-inset image-capped">

        <div class="media-body">
            <p>Current comic chapter is “${block.latest_page.chapter.title}”.</p>

            <p>Latest update is page ${block.latest_page.page_number}, posted ${libformat.format_date(block.latest_page.date_published)}!</p>

            <ul>
                <li><a href="${request.route_url('comic.page', block.chapter_cover_page)}">Read this chapter from the beginning</a></li>
                <li><a href="${request.route_url('comic.page', block.comic_first_page)}">Read this comic from the beginning</li>
                <li><a href="${request.route_url('comic.archive', block.latest_page.comic)}">Browse the archive</a></li>
            </ul>
        </div>
    </div>
</section>
</%def>
