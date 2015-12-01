<%inherit file="/_base.mako" />
<%namespace name="lib" file="/_lib.mako" />

## TODO title might be nice here instead, but we have to parse the whole page
## to get it
<%block name="title">Edit ${page.path}</%block>

<section>
    <h1>Edit /${page.path}</h1>

    <%lib:form action="">
        <p>
            <textarea class="fill" name="content" rows="30" cols="100">${raw_content}</textarea>
        </p>
        <p>
            <input type="text" name="message" size="50" placeholder="Describe your change">
            % if request.user and request.user.can('wiki', 'edit'):
            <button type="submit" name="action" value="save">Save</button>
            % endif
            % if request.user and request.user.can('wiki', 'propose'):
            <button type="submit" name="action" value="propose">Propose</button>
            % endif
        </p>
    </%lib:form>
</section>
