<!DOCTYPE html>
<html class="no-js" lang="en">
<head>
    <meta charset="utf-8">
    <%block name="head_stylesheets">
    <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='archetype')}">
    <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='layout')}">
    </%block>
    <title><%block name="title">somewhere</%block> - ${request.registry.settings.get('spline.site_title', 'spline')}</title>

    ## TODO i would not mind a more smarter javascript load system
    <script src="//ajax.googleapis.com/ajax/libs/jquery/2.1.0/jquery.min.js"></script>

    ## TODO really need some better way to handle vendored stuff like this.
    <link rel="stylesheet" type="text/css" href="${request.static_url('spline:assets/vendor/chosen-1.1.0/chosen.min.css')}">
    <script src="${request.static_url('spline:assets/vendor/chosen-1.1.0/chosen.jquery.min.js')}"></script>
    <script>
        $(function() {
            $('select').chosen();
        });
    </script>
<%block name="head_extra"></%block>
</head>
<body>
    <header>
    <%block name="main_header">
        <nav class="navbar">
            <ul class="global-nav">
                <li><a class="brand" href="${request.route_url('__core__.home')}">home</a></li>
                % for label, route_name, args, kwargs in spline_menu:
                <li><a href="${request.route_url(route_name, *args, **kwargs)}">${label}</a></li>
                % endfor

                <%block name="extra_global_nav"></%block>

                ##<li class="nav-search">
                ##    <form action="${request.route_url('__core__.search')}" method="GET">
                ##        <input type="search" name="q" placeholder="Search">
                ##    </form>
                ##</li>

                <li class="nav-auth">
                % if request.user:
                    <span class="not-a-link" id="current-user"
                        ## TODO need a better way to manage the weird
                        ## intermediate state where persona thinks we're logged
                        ## in but spline thinks we're pending
                        data-email="${request.session.get('pending_auth', {}).get('persona_email') or request.user.email}">
                        ${request.user.name}
                        ## TODO rel isn't actually valid on form; how else to do this?
                        ## TODO sigh get this style outta here.  also button
                        ## turns white-text on hover for some reason.
                        <form rel="logout" style="display: inline-block;" action="${request.route_url('__core__.auth.logout')}" method="POST">
                            <button type="submit">log out</button>
                        </form>
                    </span>
                % else:
                    <a rel="login" href="${request.route_url('__core__.auth.login')}"
                        ## TODO need a better way to manage the weird
                        ## intermediate state where persona thinks we're logged
                        ## in but spline thinks we're pending
                        id="current-user"
                        data-email="${request.session.get('pending_auth', {}).get('persona_email') or u''}">
                    log in</a>
                % endif
                </li>
            </ul>
        </nav>
    </%block>
    </header>

    <%block name="main">
    <main class="tile">
        ## TODO i increasingly dislike how rigid this structure is, and how it
        ## ends up outside any section -- impossible for a page to make multiple
        ## tiles this way.  in practice i think this gets factored out into a
        ## common intermediate base template anyway, so...
        <header>
            <nav>
                <ul>
                    <%block name="section_nav"></%block>
                </ul>
            </nav>
            <%block name="header"></%block>
        </header>

        ${next.body()}

    </main>
    </%block>

    ## Google Analytics cruft
    ## TODO /definitely/ unhardcode this nonsense
    % if 'spline.google_analytics' in request.registry.settings:
    <script>
        (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
        (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
        m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
        })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

        ## TODO er well this should be json-encoded really
        ga('create', '${request.registry.settings['spline.google_analytics']}', 'auto');
        ga('send', 'pageview');
    </script>
    % endif
</body>
</html>
