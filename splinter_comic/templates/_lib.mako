<%namespace name="libcore" file="splinter:templates/_lib.mako" />

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
