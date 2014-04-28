<%inherit file="/_base.mako"/>

<%block name="title">Register</%block>

<section>
    <h1>Register</h1>

    <form action="${request.route_url('__core__.auth.register')}" method="POST">
        <fieldset>
            <dl class="horizontal">
                <dt>Log in with</dt>
                <dd>Mozilla Persona</dd>

                <dt><label>Email</label></dt>
                <dd>
                    <code>${request.session['pending_auth']['persona_email']}</code>
                </dd>

                <dt><label>Name</label></dt>
                <dd><input type="text" name="username" value=""></dd>

                <dd><button type="submit">Register and log in</button></dd>
            </dl>
        </fieldset>
    </form>
</section>
