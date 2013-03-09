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

                <li>
                    <form action="${request.route_url('pastebin.search')}" method="GET">
                        <input type="search" name="q" placeholder="Find a paste">
                    </form>
                </li>

                <li>
                    % if user:
                        hey ${user.name}, sup
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
