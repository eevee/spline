<%inherit file="/_base.mako" />
<%namespace name="lib" file="_lib.mako" />

<%block name="title">quote db</%block>

<section>
    <h1>Quotes</h1>

    <ul>
        % for quote in quotes:
        <li>${lib.render_quote(quote)}</li>
        % endfor
    </ul>
</section>
