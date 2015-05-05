<%!
    from spline.display.rendering import render_prose
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%!
def title_for_page(page):
    if page.title:
        prefix = page.title + ' - '
    else:
        prefix = ''
    return "{prefix}{title} page for {date}".format(
        prefix=prefix,
        title=page.comic.title,
        date=format_date(page.local_date_published),
    )
%>

<%block name="title">${title_for_page(page)}</%block>


${main_section(prev_page, page, next_page, transcript)}


<%def name="main_section(prev_page, page, next_page, transcript=None)">
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

    ## XXX FLORAVERSE i am human garbage.  please make this a real feature goddamn.
    % if page.id == 292:
    <div class="comic-page-image-container">
        <iframe width="640" height="480" src="https://www.youtube.com/embed/UqrqZorg_78?rel=0" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 297:
    <div class="comic-page-image-container">
        <iframe width="800" height="600" src="http://apps.veekun.com/flora-cutscenes/#prompt2-itchyitchy-part1" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 298:
    <div class="comic-page-image-container">
        <iframe width="800" height="600" src="http://apps.veekun.com/flora-cutscenes/#prompt2-itchyitchy-part2" frameborder="0" allowfullscreen></iframe>
    </div>
    % endif

    ${draw_comic_controls(prev_page, page, next_page)}
</section>

% if transcript and transcript.exists:
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

## TODO i don't like this globally-unique id thing, though, granted, it's
## unlikely there'd be more than one disqus thread on a single page
<section class="comments">
    <h1>Comments</h1>
    <div id="disqus_thread"></div>
    <script type="text/javascript">
        ## TODO FLORAVERSE
        var disqus_shortname = 'floraverse';
        ## Note: this block might be included on pages that aren't the comic
        ## page (most notably the homepage!), so we mustn't assume the disqus
        ## defaults are okay
        ## TODO need a standard html-safe jsonify thing (or a block that changes the filter, like buck's JS?)
        ## TODO do something so that dev doesn't snag the url first?  or is that not a problem with full uri?
        <% import json %>
        var disqus_identifier = ${json.dumps(request.route_url('comic.page', page))|n};
        var disqus_url = ${json.dumps(request.route_url('comic.page', page))|n};
        var disqus_title = ${json.dumps(title_for_page(page))|n};
        (function() {
            var dsq = document.createElement('script');
            dsq.type = 'text/javascript';
            dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
</section>
</%def>


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
                ${format_date(page.local_date_published)}
            </div>
        </div>
</%def>
