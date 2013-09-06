<%!
    from splinter.format import format_date
%>
<%inherit file="splinter_comic:templates/_base.mako" />

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
    .comic-page-controls {
        margin: 1em auto;
        font-size: 2em;
    }
    .comic-page-controls a {
        text-decoration: none;
        line-height: 1;
        display: inline-block;
    }
    .comic-page-image {
        background: white;
        padding: 3px;
        border: 1px solid #606060;
        box-shadow: 0 1px 3px #808080;
    }
</style>

<section>
    <div class="comic-page">
        <h3>${page.title}</h3>
        ${draw_comic_controls(prev_page, page, next_page)}

        <img src="${request.static_url('splinter:../data/filestore/' + page.file)}"
            class="comic-page-image">

        ${draw_comic_controls(prev_page, page, next_page)}

        <div class="media-block">
            <header>
                <h1>${page.author.name}</h1>
            </header>

            ${page.comment}
        </div>

    </div>
</section>


<%def name="draw_comic_controls(prev_page, page, next_page)">
        <div class="comic-page-controls">
            % if prev_page:
                <a href="${request.route_url('comic.page', prev_page)}">◀</a>
            % else:
                ◁
            % endif

            ·
            ${format_date(page.date_published)}
            ·

            % if next_page:
                <a href="${request.route_url('comic.page', next_page)}">▶</a>
            % else:
                ▷
            % endif
        </div>
</%def>
