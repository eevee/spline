<%inherit file="/_base.mako" />

<section>
    <h1>No such page</h1>

    <p>There's no such page <code>/${path}</code> in the wiki.</p>

    <p>Perhaps you'd like to <a href="${request.route_url('wiki', '@@edit', traverse=path)}">create it?</a></p>
</section>
