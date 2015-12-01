<%inherit file="/_base.mako"/>
<%namespace name="lib" file="/_lib.mako" />

<%block name="title">♥</%block>

<section>
    <h1>Send some love</h1>

    <%lib:form action="${request.route_url('love.express')}">
        <fieldset>
            <dl class="horizontal">
                <dt><label>Send love to</label></dt>
                <dd><input type="text" name="target" value=""></dd>

                <dt><label>For</label></dt>
                <dd><input type="text" name="comment" value=""></dd>

                <dd><button type="submit">♥ ♡ ♥</button></dd>
            </dl>
        </fieldset>
    </%lib:form>
</section>
