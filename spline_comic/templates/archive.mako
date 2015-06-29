<%!
    from spline.format import format_date
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">
% if parent_folder:
    % for ancestor in parent_folder.ancestors:
        ${ancestor.title} /
    % endfor
    ${parent_folder.title} -
% endif
Archive
</%block>

<%block name="header">
% if parent_folder:
<h1>
<a href="${request.route_url('comic.archive')}">Archive</a> »
% for ancestor in parent_folder.ancestors:
<a href="${request.resource_url(ancestor)}">${ancestor.title}</a> »
% endfor
${parent_folder.title}
</h1>
% else:
<h1>Archive</h1>
% endif
</%block>

% if parent_folder:
<ul class="comic-page-grid">
% for page in parent_folder.pages:
    <li class="${'privileged' if page.is_queued else ''}">
        <a href="${request.resource_url(page)}">
            <img src="${page.file.url_from_request(request)}"
                class="image-capped">

            ${page.title or "page {}".format(page.page_number)}
        </a>
    </li>
% endfor
% for i in range(10):
<li class="-dummy"></li>
% endfor
</ul>
% endif

% for folder in folders:
% if folder.children or recent_pages_by_folder[folder]:
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

                    ${child_folder.title}
                </a>
            </li>
        % endif
    % endfor
    ## TODO not sure this ordering makes sense.  isn't the above early-first and this is recent-first?
    ## TODO do i want some separation between these?  two separate rows, perhaps?
    ## TODO really want to have a text-overflow sort of thing here
    % for page in recent_pages_by_folder[folder]:
        <li class="${'privileged' if page.is_queued else ''}">
            <a href="${request.resource_url(page)}">
                <img src="${page.file.url_from_request(request)}"
                    class="image-capped">

                ${page.title or "page {}".format(page.page_number)}
            </a>
        </li>
    % endfor
    ## Inject a row's worth of dummy zero-height elements -- this keeps the
    ## last row from filling all available space (because these items will
    ## invisibly share it)
    % for i in range(10):
    <li class="-dummy"></li>
    % endfor
    </ul>
</section>
% endif
% endfor
