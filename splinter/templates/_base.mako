<!DOCTYPE html>
<html class="no-js" lang="en">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='archetype')}">
  <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='layout')}">
  <title><%block name="title">somewhere</%block> - ${request.registry.settings.get('splinter.site_title', 'splinter')}</title>
</head>
<body>
    <header>
        <nav class="navbar">
            <ul class="global-nav">
                <li><a class="brand" href="${request.route_url('__core__.home')}">home</a></li>
                % for label, route_name, args, kwargs in splinter_menu:
                <li><a href="${request.route_url(route_name, *args, **kwargs)}">${label}</a></li>
                % endfor

                ##<li class="nav-search">
                ##    <form action="${request.route_url('__core__.search')}" method="GET">
                ##        <input type="search" name="q" placeholder="Search">
                ##    </form>
                ##</li>

                ##<li class="nav-auth">
                ##    % if request.user:
                ##        <span class="not-a-link">hey ${request.user.name}, sup</span>
                ##    % else:
                ##        <a href="${request.route_url('__core__.login')}">log in</a>
                ##    % endif
                ##</li>
            </ul>
            <ul class="section-nav">
                <%block name="section_nav"></%block>
            </ul>
        </nav>

        <%block name="header"></%block>
        <%block name="subheader"></%block>
    </header>

    <div class="main">

        ${next.body()}

    </div>
</body>
</html>
