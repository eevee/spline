<%!
    import spline.format as libfmt
    from spline.display.rendering import render_json as j
%>

## TODO wild idea: change the escape filter to allow automatically rendering
## certain types in custom ways?
<%def name="timestamp(dt)">
${dt.strftime("%a %b %d, %Y @ %H:%M")}
</%def>

<%def name="relative_timestamp(dt)"><time datetime="${dt.isoformat()}">${libfmt.format_relative_date(dt)}</time></%def>

<%def name="user(user)">
% if user:
${user.name}
% else:
## pastes only, TODO
Someone
% endif
</%def>

## TODO much of this should be the responsibility of a little html library
<%def name="form(action, method='POST', class_='', rel='', upload=False)">
<form action="${action}" method="${method}" class="${class_}" rel="${rel}"
% if upload:
enctype="multipart/form-data"
% endif
>
% if method != 'GET':
<input type="hidden" name="csrf_token" value="${request.session.get_csrf_token()}">
% endif
${caller.body()}
</form>
</%def>

<%def name="disqus(shortname, canon_url, thread_title)">
    ## TODO this gunk might be nice to have in some kind of widget thing?
    ## could be used for ads too
    ## TODO i don't like this globally-unique id thing, though, granted, it's
    ## unlikely there'd be more than one disqus thread on a single page
    <div id="disqus_thread"></div>
    <script type="text/javascript">
        var disqus_config = function () {
            ## Note: this block might be included on pages that aren't the comic
            ## page (most notably the homepage!), so we mustn't assume the disqus
            ## defaults are okay
            ## TODO do something so that dev doesn't snag the url first?  or is that not a problem with full uri?
            this.page.identifier = ${canon_url|j};
            this.page.url = ${canon_url|j};
            this.page.title = ${thread_title|j};
        };

        (function() { // DON'T EDIT BELOW THIS LINE
            var d = document, s = d.createElement('script');
            s.src = ${"//{}.disqus.com/embed.js".format(shortname)|j};
            s.setAttribute('data-timestamp', +new Date());
            (d.head || d.body).appendChild(s);
        })();
    </script>
</%def>
