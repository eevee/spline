<%!
    from calendar import day_name

    from spline.format import format_date
    from spline_comic.models import END_OF_TIME
%>
<%inherit file="spline_comic:templates/_base.mako" />

<%block name="title">Administrate ${comic.title}</%block>
<%block name="subheader"><h2>Admin</h2></%block>

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

    <form action="${request.route_url('comic.save-queue', comic)}" method="POST">
        <p>
            Queued pages are posted on:
            % for i, name in enumerate(day_name):
                <label>
                    <input type="checkbox" name="weekday" value="${i}"
                        ${u"checked" if str(i) in comic.config_queue else u""}>
                    <span class="checked-label">${name}</span>
                </label>
            % endfor
            <button type="submit">Save</button>
        </p>
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

