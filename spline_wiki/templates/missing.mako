<%inherit file="/_base.mako" />

<section>
    <h1>No such page</h1>

    <p>There's no such page <code>/${page.path}</code> in the wiki.</p>

    <p>Perhaps you'd like to <a href="${request.resource_url(page, '@@edit')}">create it?</a></p>
</section>
