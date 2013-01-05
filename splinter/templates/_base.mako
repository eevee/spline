<!DOCTYPE html>
<html class="no-js" lang="en">
<head>
  <meta charset="utf-8">
  <title><%block name="title">splinter</%block></title>
</head>
<body>
    <header>
        <nav>
            <a class="brand" href="${request.route_url('home')}">home</a>

            <form action="${request.route_url('search')}" method="GET">
                <input type="search" name="q" placeholder="Find a paste">
            </form>
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

            <li class="nav-header">Recent pastes</li>
            ##% for paste in recent_pastes:
            % for paste in []:
            <li>
                <a href="${request.route_url('view', id=paste.id)}">
                    ${paste.nice_title}, by ${paste.nice_author}
                </a>
            </li>
            % endfor
        </ul>
    </nav>

    <hr>

    <div>

        ${next.body()}

    </div>
</body>
</html>
