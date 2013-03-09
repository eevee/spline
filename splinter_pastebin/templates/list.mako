<%inherit file="/_base.mako"/>

<%block name="title">recent pastes</%block>

<section>
    <table class="pretty-table">
        <thead>
        </thead>
        <tbody>
            % for paste in pastes:
            <tr>
                <td><a href="${request.route_url('pastebin.view', id=paste.id)}">${paste.title or 'Untitled'} by ${paste.nice_author}</a></td>
            </tr>
            % endfor
        </tbody>
    </table>
</section>
