<%inherit file="/_base.mako"/>

<%block name="title">new paste</%block>

<h1>Paste a thing</h1>

<form action="${request.route_url('pastebin.list')}" method="POST">
    <textarea name="content" rows="24" cols="80"></textarea>

    <fieldset>
        <legend>meta</legend>

        <dl class="horizontal">
            <dt><label>You</label></dt>
            <dd><input type="text" name="author" value=""></dd>
        ##<input type="text" name="author" value="${guessed_name}">

            <dt><label>Title</label></dt>
            <dd><input type="text" name="title" value=""></dd>

            <dt><label>Syntax</label></dt>
            <dd>
                <select name="syntax">
                    <option value="[auto]" selected>Auto</option>
                    <option value="[none]">None</option>
                    % for lex_name, lex_aliases, lex_filetypes, lex_mimetypes in lexers:
                    <option value="${lex_aliases[0]}">${lex_name}</option>
                    % endfor
                </select>
            </dd>

            <dd><button type="submit">Paste</button></dd>
        </dl>
    </fieldset>
</form>
