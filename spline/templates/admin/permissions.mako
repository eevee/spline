<%inherit file="/_base.mako"/>

<%block name="title">Privileges</%block>

<section>
    <h1>Groups</h1>

    <ul>
        % for group in groups:
        <%
            group_privileges = {(gp.scope, gp.permission) for gp in group.group_permissions}
        %>
        <li>
            <b>${group.name}</b>
            <ul>
            % for scope, priv in all_privileges:
            <li>
                % if (scope, priv) in group_privileges:
                    <% group_privileges.remove((scope, priv)) %>
                    ${scope} / ${priv}
                    <form style="display: inline-block;" method="POST" action="${request.route_url('__core__.admin.permissions.revoke')}">
                        <input type="hidden" name="group" value="${group.id}">
                        <input type="hidden" name="scope" value="${scope}">
                        <input type="hidden" name="priv" value="${priv}">
                        <button type="submit">revoke</button>
                    </form>
                % else:
                    <s>${scope} / ${priv}</s>
                    <form style="display: inline-block;" method="POST" action="${request.route_url('__core__.admin.permissions.grant')}">
                        <input type="hidden" name="group" value="${group.id}">
                        <input type="hidden" name="scope" value="${scope}">
                        <input type="hidden" name="priv" value="${priv}">
                        <button type="submit">grant</button>
                    </form>
                % endif
                ## TODO list remaining group privs maybe?
            </li>
            % endfor
            </ul>
        </li>
        % endfor
    </ul>
</section>
