<%inherit file="/_base.mako"/>

<%block name="title">loves</%block>

<section>
    <h1>Loves</h1>

    <p><a href="${request.route_url('love.express')}">Express your love!</a></p>

    <table>
        <thead>
            <tr>
                <th>From</th>
                <th>To</th>
                <th>When</th>
                <th>For</th>
            </tr>
        </thead>
        <tbody>
          % for love in loves:
            <tr>
                <td>${love.source.name}</td>
                <td>${love.target.name}</td>
                <td>${love.timestamp}</td>
                <td>${love.comment}</td>
            </tr>
          % endfor
        </tbody>
    </table>
</section>
