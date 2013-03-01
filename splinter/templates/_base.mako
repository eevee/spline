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
                <li><a class="brand" href="${request.route_url('home')}">home</a></li>

                <li>
                    <form action="${request.route_url('search')}" method="GET">
                        <input type="search" name="q" placeholder="Find a paste">
                    </form>
                </li>
            </ul>
        </nav>
    </header>

    <nav>
        <ul>
            <li>
                <a href="${request.route_url('home')}">home</a>
            </li>
            <li>
                <a href="${request.route_url('paste')}">browse</a>
            </li>

            <li class="-header">Recent pastes</li>
            % for paste in recent_pastes:
            <li>
                <a href="${request.route_url('view', id=paste.id)}">
                    ${paste.nice_title}, by ${paste.nice_author}
                </a>
            </li>
            % endfor
        </ul>
    </nav>

    <div class="main">

        ${next.body()}

    </div>
</body>
</html>
