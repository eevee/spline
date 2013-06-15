<%namespace name="libcore" file="splinter:templates/_lib.mako" />

<%def name="render_activity(paste)">
<div class="-header">
    <div class="-timestamp"><a href="${request.route_url('pastebin.view', id=paste.id)}">${libcore.timestamp(paste.timestamp)}</a></div>
    <div class="-title">${paste.nice_title}</div>
    <div class="-user">
        ${libcore.user(paste.author)} pasted
        ${paste.lines}
        ${u'line' if paste.lines == 1 else u'lines'} of
        ${paste.syntax or u'plain text'}
    </div>
</div>
</%def>
