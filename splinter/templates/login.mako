<%inherit file="/_base.mako"/>

<%block name="title">log in</%block>

<section>
    <h1>Log in</h1>

    <form action="${request.route_url('__core__.login')}" method="POST">
        <fieldset>
            <dl class="horizontal">
                <dt><label>Name</label></dt>
                <dd><input type="text" name="username" value=""></dd>

                <dt><label>Password</label></dt>
                <dd>honor system  :)</dd>

                <dd><button type="submit">Log in</button></dd>
            </dl>
        </fieldset>
    </form>
</section>
