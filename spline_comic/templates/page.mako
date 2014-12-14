<%!
    from spline.display.rendering import render_prose
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">
    % if page.title:
    ${page.title} -
    % endif
    ${comic.title} page for ${format_date(page.date_published)}
</%block>

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

% if transcript.exists:
<section>
    ${render_prose(transcript.read())}
</section>
% endif

% if page.comment:
<section class="media-block">
    ${render_prose(page.comment)}
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
