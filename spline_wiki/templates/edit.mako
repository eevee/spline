<%inherit file="/_base.mako" />

## TODO title might be nice here instead, but we have to parse the whole page
## to get it
<%block name="title">Edit ${page.path}</%block>

<section>
    <h1>Edit ${page.path}</h1>

    <form action="" method="POST">
        <textarea name="content" rows="30" cols="100">${raw_content}</textarea>
        <input type="text" name="message" size="50" placeholder="Describe your change">
        <button>Save</button>
    </form>
</section>
