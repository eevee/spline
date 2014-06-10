<%inherit file="/_base.mako" />

<section>
    <h1>Edit ${page.path}</h1>

    <form action="" method="POST">
        <textarea name="content" rows="30" cols="100">${raw_content}</textarea>
        <input type="text" name="message" size="50" placeholder="Describe your change">
        <button>Save</button>
    </form>
</section>
