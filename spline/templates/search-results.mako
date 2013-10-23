<%inherit file="/_base.mako" />

<%block name="title">Search</%block>

<style> .highlight { font-weight: bold; } </style>

<section>
    <p>Found ${whoosh_results_count}.</p>

    <ul>
        % for result in whoosh_results:
        <li>
            ${repr(result)}
        </li>
        % endfor
    </ul>
</section>
