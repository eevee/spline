<%!
    from spline.format import format_datetime, format_filesize
%>
<%namespace name="libcore" file="spline:templates/_lib.mako" />

<%def name="paste_list(pastes)">
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
</%def>


<%def name="front_page_block(block)">
<section>
    <h1>Recent pastes</h1>
    <div class="block-body">
        ${paste_list(block.pastes)}
    </div>
</section>
</%def>
