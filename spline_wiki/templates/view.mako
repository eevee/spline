<%!
    from spline.display.rendering import render_prose
%>
<%inherit file="/_base.mako" />

<%block name="title">${content.metadata.get('title', ['Untitled'])[-1]}</%block>

<%block name="header"><h1>${content.metadata.get('title', ['Untitled'])[-1]}</h1></%block>

<%block name="section_nav">
    ## TODO would be nice to use view_execution_permitted here, too
  % if request.has_permission('edit', page):
    <li><a href="${request.resource_url(page, '@@edit')}">edit</a></li>
  % endif
    <li><a href="${request.resource_url(page, '@@history')}">history</a></li>
    ## TODO need a better list of wiki operations and whatevers here
    ## TODO translate?  talk?
    ## TODO parent?  breadcrumbs?
</%block>

## TODO TODO TODO LOL SUPER GROTESQUE HACK
## this particular floraverse page direly needs this light styling and there's
## no way to do it with pure markdown oops
% if page.path == 'characters':
<style>
    .markup img {
        display: block;
        float: right;
        margin-right: 1em;
        margin-bottom: 1em;
    }
    .markup p {
        clear: both;
    }
    ## TODO honestly this should probably be a default
    .markup h1, .markup h2 {
        clear: both;
    }
</style>
% endif

<section class="markup">
${content}
</section>
