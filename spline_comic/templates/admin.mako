<%!
    import calendar
    from datetime import timedelta

    from spline.format import format_date
    from spline_comic.models import END_OF_TIME
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">Administrate ${comic.title}</%block>

<section>
    <h1>Queue</h1>

    <p>Today's publication date is <b>${format_date(comic.current_publication_date)}</b>.</p>

    % if num_queued and last_queued.date_published < END_OF_TIME:
    <p>You have <b>${num_queued}</b> queued pages, enough to last until ${format_date(last_queued.date_published)}.</p>
    % elif num_queued:
    <p>You have <b>${num_queued}</b> queued pages, but your queue is <strong>disabled</strong>.  No new pages will be posted until you add one manually or enable queuing.</p>
    % else:
    <p>Your queue is empty.  No new pages will be posted until you add more.</p>
    % endif

    <style>
    .calendar {
        margin-bottom: 1em;

        text-align: center;
    }
    .calendar td {
        width: 2em;
        border: 1px solid #e0e0e0;
    }
    .calendar .calendar-month-0 {
        background: white;
    }
    .calendar .calendar-month-1 {
        background: #f6f6f6;
    }
    .calendar .calendar-month-name {
        transform: rotate(-90deg);
    }
    .calendar .calendar-today {
        background: hsl(60, 100%, 70%);
    }
    </style>
    <form action="${request.route_url('comic.save-queue', comic)}" method="POST">
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
                            <a href="${request.route_url('comic.page', day_to_page[calendar_date])}">
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
    </form>
</section>

<section>
    <h1>Upload</h1>

    <form action="${request.route_url('comic.upload', comic)}" method="POST" enctype="multipart/form-data">
        <fieldset>
            <dl class="vertical">
                <dd><input type="file" name="file"></dd>

                <dt>Title</dt>
                <dd><input type="text" name="title"></dd>

                <dt>Chapter</dt>
                <dd>
                    <ul>
                      % for chapter in chapters:
                        <li><label>
                            <input type="radio" name="chapter" value="${chapter.id}"
                                % if loop.first:
                                checked
                                % endif
                            >
                            <span class="checked-label">${chapter.title}</span>
                        </label></li>
                      % endfor
                    </ul>
                </dd>

                <dt>Commentary</dt>
                <dd><textarea name="comment"></textarea></dd>

                <dd>
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
                </dd>
                <dd>
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
                </dd>
            </dl>

            <footer><button type="submit">Upload and add to queue</button></footer>
        </fieldset>
    </form>
</section>

