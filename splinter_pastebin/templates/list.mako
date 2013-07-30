<%!
    from splinter.format import format_datetime, format_filesize
%>
<%inherit file="/_base.mako"/>

<%block name="title">pastes</%block>

<section>
    <p><a href="${request.route_url('pastebin.new')}">Paste something</a></p>
</section>

<section>
    <h1>Recent pastes</h1>

    <table class="table table-striped table-hover">
        <tbody>
            % for paste in pastes:
            <tr>
                <td><a href="${request.route_url('pastebin.view', id=paste.id)}">${paste.nice_title}</a></td>
                <td>${paste.nice_author}</td>
                <td>${paste.nice_syntax}</td>
                <td>${format_filesize(paste.size)}</td>
                <td>${paste.lines}</td>
                <td>${format_datetime(paste.timestamp)}</td>
            </tr>
            % endfor
        </tbody>
    </table>
</section>
