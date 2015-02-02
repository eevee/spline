<%!
    from pyramid.security import view_execution_permitted
%>
<%inherit file="/_base.mako" />

<%block name="head_stylesheets">
${parent.head_stylesheets()}
    <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='comic')}">
</%block>

<%block name="header"><h1>${comic.title}</h1></%block>

<%block name="section_nav">
    <li><a href="${request.route_url('comic.most-recent', comic)}">latest page</a></li>
    <li><a href="${request.route_url('comic.archive', comic)}">archives</a></li>
    ## TODO would be nice to use view_execution_permitted here
    % if request.has_permission('admin', comic):
    <li><form action="${request.route_url('comic.admin', comic)}" method="GET"><button class="warning">admin</button></form></li>
    % endif
</%block>

${next.body()}
