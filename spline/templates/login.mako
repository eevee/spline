<%inherit file="/_base.mako"/>
<%namespace name="lib" file="/_lib.mako" />

<%block name="title">log in</%block>

<section>
    <h1>Log in</h1>

    <%lib:form action="">
        <fieldset>
            <dl class="horizontal">
                <dt><label>Name</label></dt>
                <dd><input type="text" name="username" value=""></dd>

                <dt><label>Password</label></dt>
                <dd><input type="password" name="password" value=""></dd>

                <dd><button type="submit">Log in</button></dd>
            </dl>
        </fieldset>
    </%lib:form>
</section>
