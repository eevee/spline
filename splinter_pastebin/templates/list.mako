<%inherit file="/_base.mako"/>

<%block name="title">recent pastes</%block>

<ol>
    % for paste in pastes:
    <li>
        <p><a href="${request.route_url('pastebin.view', id=paste.id)}">${paste.title or 'Untitled'} by ${paste.author or u'Anonymous Coward'}</a></p>
    </li>
    % endfor
</ol>
