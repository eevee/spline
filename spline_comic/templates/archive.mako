<%!
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">Archive</%block>

<%block name="header">Archive » <h1>${request.context}</h1></%block>

% for folder in folders:
<section>
    <h1 id="comic-${folder.title_slug}">
        <a href="${request.resource_url(folder)}">${folder.title}</a>
        ## Won't be in the dict if the folder is empty!
        % if folder in date_range_by_folder:
            <span class="unheader">${format_date(date_range_by_folder[folder][0])} – ${format_date(date_range_by_folder[folder][1])}</span>
        % endif
    </h1>

    <ul class="comic-page-grid">
    % for child_folder in folder.children:
        <% page = first_page_by_folder.get(child_folder) %>
        % if page:
            ## If the first page is hidden, the whole folder (probably) is
            <li class="chapter ${'privileged' if page.is_queued else ''}">
                ## TODO this should prooobably link to the archive for the /folder/
                <a href="${request.resource_url(child_folder)}">
                    <img src="${page.file.url_from_request(request)}"
                        class="image-capped">
                </a>
            </li>
        % endif
    % endfor
    ...
    ## TODO not sure this ordering makes sense.  isn't the above early-first and this is recent-first?
    ## TODO do i want some separation between these?  two separate rows, perhaps?
    ## TODO really want to have a text-overflow sort of thing here
    % for page in recent_pages_by_folder[folder]:
        <li class="${'privileged' if page.is_queued else ''}">
            <a href="${request.resource_url(page)}">
                <img src="${page.file.url_from_request(request)}"
                    class="image-capped">
            </a>
        </li>
    % endfor
    </ul>
</section>
% endfor
