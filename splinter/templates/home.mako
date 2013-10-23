<%inherit file="/_base.mako"/>

<%block name="title">home</%block>

<section>
    <h1>Recent activity</h1>

    <ol class="activity-feed">
        % for activitum in activity:
        <li>
            <% activitum.renderer.implementation().get_def(activitum.renderer.defname).render_context(context, activitum.source) %>
        </li>
        % endfor
    </ol>
</section>

<%namespace name="librendering" module="splinter.display.rendering" />

% for block in layout.blocks:
    ${librendering.render_with_context(block.renderer, block)}
% endfor
