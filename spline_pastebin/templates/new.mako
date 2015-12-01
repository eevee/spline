<%inherit file="/_base.mako"/>
<%namespace name="lib" file="/_lib.mako" />

<%block name="title">new paste</%block>

<section>
    <h1>Paste a thing</h1>

    <%lib:form action="${request.route_url('pastebin.new')}">
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
                        <option disabled></option>
                        % for name, alias in lexers:
                        <option value="${alias}">${name}</option>
                        % endfor
                    </select>
                </dd>

                <dd><button type="submit">Paste</button></dd>
            </dl>
        </fieldset>
    </%lib:form>
</section>
