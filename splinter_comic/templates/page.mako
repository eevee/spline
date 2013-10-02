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

<%block name="subheader">
  % if page.title:
    <h2>${page.title}</h2>
  % endif
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
        margin: 0 auto;
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
        xline-height: 2;
    }
    .comic-page-image {
        background: white;
        margin: 1em;
        padding: 3px;
        border: 1px solid #606060;
        box-shadow: 0 1px 3px #808080;
    }
</style>

<section class="comic-page">
    ${draw_comic_controls(prev_page, page, next_page)}

    <img src="${request.static_url('splinter:../data/filestore/' + page.file)}"
        class="comic-page-image">

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
                <br>
                Chapter: ${page.chapter.title}
            </div>
        </div>
</%def>
