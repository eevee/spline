<%inherit file="/_base.mako"/>

<%block name="title">♥</%block>

<section>
    <h1>Send some love</h1>

    <form action="${request.route_url('love.express')}" method="POST">
        <fieldset>
            <dl class="horizontal">
                <dt><label>Send love to</label></dt>
                <dd><input type="text" name="target" value=""></dd>

                <dt><label>For</label></dt>
                <dd><input type="text" name="comment" value=""></dd>

                <dd><button type="submit">♥ ♡ ♥</button></dd>
            </dl>
        </fieldset>
    </form>
</section>
