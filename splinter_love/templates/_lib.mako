<%namespace name="libcore" file="splinter:templates/_lib.mako" />

<%def name="render_activity(love)">
<div class="-header">
    <div class="-timestamp">${libcore.timestamp(love.timestamp)}</div>
    <div class="-user">
        ${libcore.user(love.source)} loves ${libcore.user(love.target)}
    </div>
</div>
<div class="-body">
    ${love.comment}
</div>
</%def>
