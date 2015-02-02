<%inherit file="spline:templates/_base.mako"/>

<%block name="head_extra">
    ${parent.head_extra()}
    <link rel="icon" type="image/png" href="${request.static_url('spline:assets/images/favicon.png')}">
    <script src="http://ads.thehiveworks.com/delivery/spcjs.php?id=118"></script>
</%block>


<%block name="main_header">
    <div class="floraverse-header">
        <div class="floraverse-bush-left">
            <img src="/static/images/global-bush-left.png">
            <img src="/static/images/global-bush-words-left.png" alt="Also on:" class="floraverse-bush-words">

            <a href="http://floraverse.deviantart.com/" title="deviantArt" class="floraverse-button floraverse-button-deviantart">
                <img src="/static/images/global-button-deviantart-flower.png">
                <img src="/static/images/global-button-deviantart-logo.png" alt="deviantArt">
            </a>
            <a href="https://twitter.com/floraverse" title="Twitter" class="floraverse-button floraverse-button-twitter">
                <img src="/static/images/global-button-twitter-flower.png">
                <img src="/static/images/global-button-twitter-logo.png" alt="Twitter">
            </a>
            <a href="http://floraverse.tumblr.com/" title="Tumblr" class="floraverse-button floraverse-button-tumblr">
                <img src="/static/images/global-button-tumblr-flower.png">
                <img src="/static/images/global-button-tumblr-logo.png" alt="Tumblr">
            </a>
            <a href="https://www.patreon.com/floraverse" title="Patreon" class="floraverse-button floraverse-button-patreon">
                <img src="/static/images/global-button-patreon-flower.png">
                <img src="/static/images/global-button-patreon-logo.png" alt="Patreon">
            </a>
            <a href="https://www.facebook.com/floraverse" title="Facebook" class="floraverse-button floraverse-button-facebook">
                <img src="/static/images/global-button-facebook-flower.png">
                <img src="/static/images/global-button-facebook-logo.png" alt="Facebook">
            </a>
        </div>
        <div class="floraverse-banner">
            <img src="${request.static_url('spline:assets/images/global-banner.png')}">
            <nav class="floraverse-navbar">
                <ul class="inline plain">
                    <li><a href="/"><img src="/static/images/global-nav-home.png" alt="home"></a></li>
                    <li><a href="/characters"><img src="/static/images/global-nav-characters.png" alt="characters"></a></li>
                    ## XXX this is hardcoded...  but maybe that's okay
                    <li><a href="/comic/flora/archive/"><img src="/static/images/global-nav-archive.png" alt="archive"></a></li>
                    <li><a href="/about"><img src="/static/images/global-nav-about.png" alt="about"></a></li>
                    <li><a href="/contact"><img src="/static/images/global-nav-contact.png" alt="contact"></a></li>
                    <li><a href="/chatroom"><img src="/static/images/global-nav-chatroom.png" alt="chatroom"></a></li>
                </ul>
            </nav>
        </div>
        <div class="floraverse-bush-right">
            <img src="/static/images/global-bush-right.png">
            <img src="/static/images/global-bush-words-right.png" alt="Updates Monday/Wednesday/Friday" class="floraverse-bush-words">

            <a href="/rss" title="RSS" class="floraverse-button floraverse-button-rss">
                <img src="/static/images/global-button-rss-flower.png">
                <img src="/static/images/global-button-rss-logo.png" alt="RSS">
            </a>
        </div>
    </div>
</%block>

<%block name="extra_global_nav">
    ${parent.extra_global_nav()}
    <li><a href="irc://irc.veekun.com/floraverse">Chat</a></li>
    <li><a href="http://papayakitty.com/floracast/">Podcast</a></li>
</%block>

<%block name="main">
    <div class="ad ad-728x90">
        <script>/* [id321] www.floraverse.com - leader */ OA_show(321);</script><noscript><a target="_blank" href="http://ads.thehiveworks.com/delivery/ck.php?n=dda9649"><img border="0" alt="" src="http://ads.thehiveworks.com/delivery/avw.php?zoneid=321&amp;n=dda9649"></a></noscript>
    </div>
    ${parent.main()}
</%block>

${next.body()}
