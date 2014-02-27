<%!
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">
    % if page.title:
    ${page.title} -
    % endif
    ${comic.title} page for ${format_date(page.date_published)}
</%block>

<style type="text/css">
    .comic-page {
        margin: 1em auto;
        text-align: center;
    }
    .comic-page h3 {
        font-size: 1.5em;
        margin: 0;
        font-family: serif;
        font-weight: normal;
    }
    .comic-page-controls {
        width: 600px;
        margin: 1em auto;
        text-align: center;
    }
    .comic-page-controls .-prev,
    .comic-page-controls .-next {
        font-size: 2em;
        line-height: 1;
        display: inline-block;
        color: #999;
    }
    .comic-page-controls .-prev {
        float: left;
    }
    .comic-page-controls .-next {
        float: right;
    }
    .comic-page-controls .-prev a,
    .comic-page-controls .-next a {
        text-decoration: none;
    }
    .comic-page-controls .-date {
        line-height: 2;
    }
    .comic-page-image-container {
        display: flex;
        /* Fallback for browsers without min-content; little janky, though.
         * TODO is there any better way to do this?  at all? */
        width: 800px;
        width: -moz-min-content;
        width: -webkit-min-content;
        width: min-content;
        min-width: 600px;
        flex-direction: column;
        align-items: center;
        margin: 1em auto;
    }
    .comic-page-image {
        background: white;
        padding: 3px;
        border: 1px solid hsl(0, 0%, 90%);
        box-shadow: 0 1px 3px hsl(0, 0%, 90%);
    }
    .comic-page-meta {
        align-self: stretch;
        display: flex;
        margin-top: 0.33em;
        justify-content: space-between;
    }
    .comic-page-meta > .-title {
        text-align: left;
        font-style: italic;
    }
</style>

<section class="comic-page">
    ${draw_comic_controls(prev_page, page, next_page)}

    <div class="comic-page-image-container">
        <img src="${page.file.url_from_request(request)}"
            class="comic-page-image">

        <div class="comic-page-meta">
            <div class="-title">
              % if page.title:
                <q>${page.title}</q>
              % endif
            </div>
            <div class="-chapter-page">
                <a href="${request.route_url('comic.archive', page.comic)}#chapter-${page.chapter.title_slug}">${page.chapter.title}</a>, page ${page.page_number}
            </div>
        </div>
    </div>

    ${draw_comic_controls(prev_page, page, next_page)}
</section>

% if page.comment:
<section class="media-block">
    <p>${page.comment}</p>
    —<em>${page.author.name}</em>
</section>
% endif


<%def name="draw_comic_controls(prev_page, page, next_page)">
        <div class="comic-page-controls">
            <div class="-prev">
              % if prev_page:
                <a href="${request.route_url('comic.page', prev_page)}">◀ back</a>
              % else:
                ◁ back
              % endif
            </div>

            <div class="-next">
              % if next_page:
                <a href="${request.route_url('comic.page', next_page)}">next ▶</a>
              % else:
                next ▷
              % endif
            </div>

            <div class="-date">
                ${format_date(page.date_published)}
            </div>
        </div>
</%def>
