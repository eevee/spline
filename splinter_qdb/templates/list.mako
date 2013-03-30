<%inherit file="/_base.mako" />

<%block name="title">quote db</%block>

<section>
    <h1>Quotes</h1>

    <ul>
        % for quote in quotes:
        <li>
            <pre>${quote.content}</pre>
            <p>
                kudos ${quote.poster.name}
                % if quote.comment:
                    — “${quote.comment}”
                % endif
            </p>
            <p>${quote.timestamp}</p>
        </li>
        % endfor
    </ul>
</section>
