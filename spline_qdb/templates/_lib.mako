<%namespace name="libcore" file="spline:templates/_lib.mako" />

################################################################################
## Spline API

<%def name="render_activity(quote)">
<div class="-header">
    <div class="-timestamp"><a href="${request.route_url('qdb.view', id=quote.id)}">${libcore.timestamp(quote.timestamp)}</a></div>
  % if quote.comment:
    <div class="-title">${quote.comment}</div>
  % endif
    <div class="-user">
        ${libcore.user(quote.poster)} added a quote
    </div>
</div>
<div class="-body">
    <pre>${quote.content}</pre>
</div>
</%def>

################################################################################

<%def name="render_quote(quote)">
    <pre>${quote.content}</pre>
    <p>
        kudos ${quote.poster.name}
        % if quote.comment:
            — “${quote.comment}”
        % endif
    </p>
</%def>
