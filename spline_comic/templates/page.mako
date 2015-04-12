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


${main_section(page, adjacent_pages, transcript)}


<%def name="main_section(page, adjacent_pages, transcript=None)">
<section class="comic-page">
    ${draw_comic_controls(page, adjacent_pages)}

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
    % elif page.id == 299:
    <div class="comic-page-image-container">
        <iframe width="800" height="600" src="http://apps.veekun.com/flora-cutscenes/#prompt2-itchyitchy-part3" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 300:
    <div class="comic-page-image-container">
        <iframe width="800" height="600" src="http://apps.veekun.com/flora-cutscenes/#prompt2-itchyitchy-part4" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 301:
    <div class="comic-page-image-container">
        <iframe width="640" height="480" src="https://www.youtube.com/embed/2DlzC2eAhOo?rel=0" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 303:
    <div class="comic-page-image-container">
        <iframe width="640" height="480" src="https://www.youtube.com/embed/Ii2ZYqP8vOU?rel=0" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 304:
    <div class="comic-page-image-container">
        <iframe width="800" height="600" src="http://apps.veekun.com/flora-cutscenes/#prompt2-itchyitchy-final" frameborder="0" allowfullscreen></iframe>
    </div>
    % elif page.id == 307:
    <div class="comic-page-image-container">
        <iframe width="800" height="600" src="http://apps.veekun.com/flora-cutscenes/#brokentoy-part1" frameborder="0" allowfullscreen></iframe>
    </div>
    % endif

    ${draw_comic_controls(page, adjacent_pages)}
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


<%def name="_maybe_page_link(page, yes_label, no_label)">
% if page is None:
${no_label}
% else:
<a href="${request.route_url('comic.page', page)}">${yes_label}</a>
% endif
</%def>

<%def name="draw_comic_controls(page, adjacent_pages)">
    <div class="comic-page-controls">
      % if adjacent_pages.prev_by_date == adjacent_pages.prev_by_story:
        <div class="-prev -combined">
            ${_maybe_page_link(adjacent_pages.prev_by_date, '◀ previous', '◁ previous')}
        </div>
      % else:
        <div class="-prev">
            ${_maybe_page_link(adjacent_pages.prev_by_date, '◀ previous by date', '◁ previous by date')}
            ${_maybe_page_link(adjacent_pages.prev_by_story, '◀ previous by story', '◁ previous by story')}
        </div>
      % endif

        <div class="-date">
            ${format_date(page.local_date_published)}
        </div>

      % if adjacent_pages.next_by_date == adjacent_pages.next_by_story:
        <div class="-next -combined">
            ${_maybe_page_link(adjacent_pages.next_by_date, 'next ▶', 'next ▷')}
        </div>
      % else:
        <div class="-next">
            ${_maybe_page_link(adjacent_pages.next_by_date, 'next by date ▶', 'next by date ▷')}
            ${_maybe_page_link(adjacent_pages.next_by_story, 'next by story ▶', 'next by story ▷')}
        </div>
      % endif
    </div>
</%def>
