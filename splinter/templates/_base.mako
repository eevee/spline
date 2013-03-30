<!DOCTYPE html>
<html class="no-js" lang="en">
<head>
  <meta charset="utf-8">
  <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='archetype')}">
  <link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='layout')}">
  <title><%block name="title">somewhere</%block> - splinter</title>
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a class="brand" href="${request.route_url('__core__.home')}">home</a></li>
                <li><a href="${request.route_url('pastebin.list')}">pastes</a></li>
                <li><a href="${request.route_url('love.list')}">love</a></li>
                <li><a href="${request.route_url('qdb.list')}">qdb</a></li>

                <li class="nav-search">
                    <form action="${request.route_url('pastebin.search')}" method="GET">
                        <input type="search" name="q" placeholder="Search">
                    </form>
                </li>

                <li class="nav-auth">
                    % if request.user:
                        <span class="not-a-link">hey ${request.user.name}, sup</span>
                    % else:
                        <a href="${request.route_url('__core__.login')}">log in</a>
                    % endif
                </li>
            </ul>
        </nav>
    </header>

    <div class="main">

        ${next.body()}

    </div>
</body>
</html>
