<%inherit file="/_base.mako" />

<%block name="title">find pastes</%block>

<style> .highlight { font-weight: bold; } </style>

<p>Found ${len(results)}.</p>

<ul>
    % for paste, fragments, title in results:
    <li>
        <p><a href="${request.route_url('view', id=paste.id)}">${paste.nice_title} by ${paste.nice_author}</a></p>
        % for frag in fragments:
            <p>… ${frag | n} …</p>
        % endfor
    </li>
    % endfor
</ul>
