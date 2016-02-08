<%namespace name="libcore" file="spline:templates/_lib.mako" />
<%!
    import spline.format as libformat
    from spline.display.rendering import render_prose
    from spline.display.rendering import trim_html
%>

<%def name="render_activity(page)">
<div class="-header">
    <div class="-timestamp">${libcore.timestamp(page.date_published)}</div>
    <div class="-title">
        <a href="${request.resource_url(page)}">${page.title or u'untitled'}</a>
    </div>
    <div class="-user-etc">
        new comic page for ${page.comic.title}
        <br>
        posted by ${libcore.user(page.author)}
    </div>
</div>
</%def>

## Render a thumbnail for a GalleryItem
<%def name="thumbnail(item)">
## TODO this heavily assumes the first item is an image, fix please <3
<img src="${item.media[0].thumbnail_file.url_from_request(request)}" class="image-capped">
</%def>


<%def name="front_page_block(block)">
## TODO not sure how to handle this; maybe i want to inject into global css
<style>@import url(${request.route_url('pyscss', css_path='comic')});</style>

<section>
    <h1>Latest pages</h1>
    % for page in block.recent_pages:
    <div class="comic-block block-body media">
        <a class="media-inset" href="${request.resource_url(page)}">
            ${thumbnail(page)}
        </a>

        <div class="media-body media-body--with-footer">
            <div class="media-body-main">
                <p style="float: right;">
                    ${libformat.format_relative_date(page.date_published)}
                    ·
                    in <a href="${request.resource_url(page.chapter)}">
                        ${page.chapter.title}
                    </a>
                </p>
                <p>
                    <a href="${request.resource_url(page)}">
                        % if page.title:
                            “${page.title}”
                        % else:
                            untitled
                        % endif
                    </a>
                </p>
                <div class="prose">
                    ${trim_html(render_prose(page.comment))}
                </div>
                <p>
                    —<em>${page.author.name}</em>
                </p>
            </div>
        </div>
    </div>
    % endfor
    <p><a href="${request.route_url('comic.archive')}">See more in the archives</a></p>
</section>
</%def>
