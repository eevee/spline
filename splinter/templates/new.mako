<%inherit file="/_base.mako"/>

<%block name="title">new paste</%block>

<h1>Paste a thing</h1>

<form action="${request.route_url('paste')}" method="POST">
    <textarea name="content" rows="20" cols="200"></textarea>

    <hr>
<fieldset>

    <label>You</label>
    ##<input type="text" name="author" value="${guessed_name}">
    <input type="text" name="author" value="">

    <label>Title</label>
    <input type="text" name="title" value="">

    <label>Syntax</label>
    <select name="syntax">
        <option value="[auto]" selected>Auto</option>
        <option value="[none]">None</option>
        % for lex_name, lex_aliases, lex_filetypes, lex_mimetypes in lexers:
        <option value="${lex_aliases[0]}">${lex_name}</option>
        % endfor
    </select>

    <button type="submit">Paste</button>
</fieldset>
</form>
