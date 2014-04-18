<%inherit file="/_base.mako"/>
<%namespace name="lib" file="spline_pastebin:templates/_lib.mako" />

<%block name="title">pastes</%block>

<section>
    <p><a href="${request.route_url('pastebin.new')}">Paste something</a></p>
</section>

<section>
    <h1>Recent pastes</h1>
    ${lib.paste_list(pastes)}
</section>
