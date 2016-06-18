<%!
    import calendar
    from datetime import timedelta

    from spline.format import format_date
    from spline_comic.models import END_OF_TIME
    from spline_comic.models import get_current_publication_date
    from spline_comic.models import XXX_HARDCODED_TIMEZONE
%>
<%inherit file="spline_comic:templates/_base.mako" />
<%namespace name="lib" file="/_lib.mako" />

<%block name="head_extra">
    <script src="${request.static_url('spline_comic:assets/js/admin.js')}"></script>
    ${parent.head_extra()}
</%block>

<%block name="title">Administrate gallery</%block>

<section>
    <h1>Queue</h1>

    <p>Today's publication date is <b>${format_date(get_current_publication_date(XXX_HARDCODED_TIMEZONE))}</b>.</p>

    % if num_queued and last_queued.date_published < END_OF_TIME:
    <p>You have <b>${num_queued}</b> queued pages, enough to last until ${format_date(last_queued.local_date_published)}.</p>
    % elif num_queued:
    <p>You have <b>${num_queued}</b> queued pages, but your queue is <strong>disabled</strong>.  No new pages will be posted until you add one manually or enable queuing.</p>
    % else:
    <p>Your queue is empty.  No new pages will be posted until you add more.</p>
    % endif

    <%lib:form action="${request.route_url('comic.save-queue')}">
        <table class="calendar comic-calendar">
            <caption>Post queued pages on:</caption>
            <thead>
                <tr>
                    ## TODO don't use calendar module for this; we never setlocale()
                    <th></th>
                    % for wd in (6, 0, 1, 2, 3, 4, 5):
                    <th>
                        <label>
                            <input type="checkbox" name="weekday" value="${wd}"
                                ${u"checked" if str(wd) in comic.config_queue else u""}>
                            <span class="checked-label"><br>${calendar.day_abbr[wd]}</span>
                        </label>
                    </th>
                    % endfor
                </tr>
            </thead>
            <% calendar_date = calendar_start %>
            <% seen_ym = set() %>
            <tbody>
                % while calendar_date <= calendar_end:
                <tr>
                    <% ym = calendar_date.year, calendar_date.month %>
                    % if ym not in seen_ym:
                        <%! import math %>
                        <%
                            seen_ym.add(ym)
                            if ym == (calendar_end.year, calendar_end.month):
                                lastday = calendar_end.day
                            else:
                                __, lastday = calendar.monthrange(*ym)

                            weeks = int(math.ceil((lastday - calendar_date.day + 1) / 7))
                        %>
                        <th rowspan="${weeks}" class="calendar-month-${calendar_date.month % 2}">
                            % if weeks > 1:
                            <div class="calendar-month-name">${calendar.month_abbr[calendar_date.month]}</div>
                            % endif
                        </th>
                    % endif
                    % for day in range(7):
                        <td class="
                            calendar-month-${calendar_date.month % 2}
                            % if calendar_date == comic.current_publication_date.date():
                            calendar-today
                            % endif
                        ">
                            % if calendar_date in day_to_page:
                            <a href="${request.resource_url(day_to_page[calendar_date])}">
                            ${calendar_date.day}
                            </a>
                            % else:
                            ${calendar_date.day}
                            % endif
                        </td>
                        <% calendar_date += timedelta(days=1) %>
                    % endfor
                </tr>
                % endwhile
            </tbody>
        </table>
        <p><button type="submit">Save and update queue</button></p>
    </%lib:form>
</section>

<section>
    <h1>Upload</h1>

    <%lib:form action="${request.route_url('comic.upload')}" upload="${True}">
        <fieldset>
            <p><input type="file" name="file"></p>
            <p><input type="text" name="title" placeholder="Title (optional)"></p>

            <p>
                Chapter: <select name="chapter">
                  <% stack = [] %>
                  % for chapter in chapters:
                    <%
                        while stack and chapter.left > stack[-1].right:
                            stack.pop()
                        stack.append(chapter)
                    %>
                    <option value="${chapter.id}"
                            % if loop.first:
                            selected
                            % endif
                        >
                        % for _ in range(len(stack) - 1):
                        &nbsp;&nbsp;
                        % endfor
                        ${chapter.title}
                    </option>
                  % endfor
                </select>
            </p>

            <div class="js-markdown-preview">
                <textarea name="comment" placeholder="Comment (optional)"></textarea>
            </div>

            <p>
                Optional iframe (e.g., YouTube): <br>
                <input type="text" name="iframe_url" size="40" placeholder="URL">
                <input type="text" name="iframe_width" size="3" value="800">
                × <input type="text" name="iframe_height" size="3" value="600">
            </p>

            <p>
                <label>
                    <input type="radio" name="when" value="queue" checked>
                    <span class="checked-label">
                        % if queue_next_date:
                        Add this page to your queue, to be published on ${format_date(queue_next_date)}.
                        % else:
                        Add this page to your queue.  It will not be published until you select queue dates above.
                        % endif
                    </span>
                </label>
            </p>
            <p>
                <label>
                    <input type="radio" name="when" value="now">
                    <span class="checked-label">
                        % if num_queued:
                        Publish this page now, ahead of the ${num_queued} pages in your queue.
                        % else:
                        Publish this page now.
                        % endif
                    </span>
                </label>
            </p>

            <footer><button type="submit">Upload and add to queue</button></footer>
        </fieldset>
    </%lib:form>
</section>

<section id="manage-folders">
    <h1>Manage folders</h1>
    <p>Wow this isn't done at all!  In fact it's probably totally broken, maybe don't use it.</p>
    <%lib:form action="${request.route_url('comic.admin.folders')}">
    <ul>
    <% last = None %>
    <% ancestry = [] %>
    % for folder in chapters:
        <%
            if last and last.right > folder.left:
                ancestry.append(last)
            while ancestry and ancestry[-1].right < folder.left:
                ancestry.pop()
        %>
        <li>
            % for _ in ancestry:
                —
            % endfor
            ${folder.id} | ${folder.left} ${folder.right} ${folder.title} ${folder.ancestors}
            <button type="submit" name="${folder.id}" value="right">
                ↓</button>
            <button type="submit" name="${folder.id}" value="left">
                ↑</button>
        </li>
        <% last = folder %>
    % endfor
    </ul>
    </%lib:form>
</section>
