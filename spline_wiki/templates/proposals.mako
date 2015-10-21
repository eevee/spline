<%inherit file="/_base.mako" />

## TODO title might be nice here instead, but we have to parse the whole page
## to get it
<%block name="title">Proposed changes to ${page.path}</%block>

<section>
<ul>
    % for branch_name, proposer in page.iter_branches('proposals/'):
    <li>
        <form action="
    % endfor
</ul>
</section>
