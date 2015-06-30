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

<%block name="header">
<p>
    % for ancestor in page.folder.ancestors:
        <a href="${request.resource_url(ancestor)}">${ancestor.title}</a> »
    % endfor
    <a href="${request.resource_url(page.folder)}">${page.folder.title}</a> »
</p>
<h1>${page.title or "page {}".format(page.page_number)}</h1>
</%block>


${main_section(page, adjacent_pages, transcript)}


<%def name="main_section(page, adjacent_pages, transcript=None)">
<section class="comic-page">
    ${draw_comic_controls(page, adjacent_pages)}

    % for medium in page.media:
    <div class="comic-page-image-container">
        % if medium.discriminator == 'image':
            <img src="${medium.image_file.url_from_request(request)}"
                class="comic-page-image">
        % elif medium.discriminator == 'iframe':
            <iframe width="${medium.width}" height="${medium.height}" src="${medium.url}" frameborder="0" allowfullscreen></iframe>
        % endif
    </div>
    % endfor

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
        var disqus_identifier = ${json.dumps(request.resource_url(page))|n};
        var disqus_url = ${json.dumps(request.resource_url(page))|n};
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
<a href="${request.resource_url(page)}">${yes_label}</a>
% endif
</%def>

<%def name="draw_comic_controls(page, adjacent_pages)">
    ## TODO these should indicate when you're going to jump the border of a folder
    <div class="comic-page-controls">
      % if adjacent_pages.prev_by_date == adjacent_pages.prev_by_story:
        <div class="-prev -combined">
            ${_maybe_page_link(adjacent_pages.prev_by_date, '◀ previous', '◁ first')}
        </div>
      % else:
        <div class="-prev">
            ${_maybe_page_link(adjacent_pages.prev_by_date, '◀ previous by date', '◁ first by date')}
            ${_maybe_page_link(adjacent_pages.prev_by_story, '◀ previous by story', '◁ last by story')}
        </div>
      % endif

        <div class="-date">
            ${format_date(page.local_date_published)}
        </div>

      % if adjacent_pages.next_by_date == adjacent_pages.next_by_story:
        <div class="-next -combined">
            ${_maybe_page_link(adjacent_pages.next_by_date, 'next ▶', 'last ▷')}
        </div>
      % else:
        <div class="-next">
            ${_maybe_page_link(adjacent_pages.next_by_date, 'next by date ▶', 'last by date ▷')}
            ${_maybe_page_link(adjacent_pages.next_by_story, 'next by story ▶', 'last by story ▷')}
        </div>
      % endif
    </div>
</%def>
