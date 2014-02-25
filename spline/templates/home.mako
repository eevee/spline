<%inherit file="/_base.mako"/>

<%block name="title">home</%block>

## TODO un-hardcode these two
<%block name="head_extra">
    <link rel="alternate" type="application/atom+xml" href="/@@feed">
</%block>
## TODO figure out a better story for icons; turn them into data: uris?
<%block name="section_nav">
    <li><a href="/@@feed"><img src="/static/images/fugue-icons/feed.png"> RSS</a></li>
</%block>

<%block name="header"><h1>${request.registry.settings['spline.site_title']}</h1></%block>

## TODO once blocks are figured out, deprecate this junk and port everything away from it
% for activitum in activity:
<section>
    <% activitum.renderer.implementation().get_def(activitum.renderer.defname).render_context(context, activitum.source) %>
</section>
% endfor

<%namespace name="librendering" module="spline.display.rendering" />

% for block in layout.blocks:
    ${librendering.render_with_context(block.renderer, block)}
% endfor
