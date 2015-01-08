<%inherit file="spline:templates/_base.mako"/>

<%block name="head_extra">
    ${parent.head_extra()}
    <link rel="icon" type="image/png" href="${request.static_url('spline:assets/images/favicon.png')}">
</%block>

<%block name="main_header">
    ${parent.main_header()}

    <img src="http://papayakitty.com/stayout/flora/florasitebannertransr.png" style="display: block; margin: 0.5rem auto;">
</%block>

<%block name="extra_global_nav">
    ${parent.extra_global_nav()}
    <li><a href="http://floraverse.deviantart.com/">deviantArt</a></li>
    <li><a href="irc://irc.veekun.com/floraverse">Chat</a></li>
    <li><a href="http://floraverse.tumblr.com/">Tumblr</a></li>
    <li><a href="http://papayakitty.com/floracast/">Podcast</a></li>
    <li><a href="http://www.patreon.com/floraverse">Support us</a></li>
</%block>

${next.body()}
