<%inherit file="spline:templates/home.mako"/>

<%block name="main">
<main class="front-page-layout">
<div class="front-page-main">
    <div class="ad ad-728x90">
        <script>/* [id321] www.floraverse.com - leader */ OA_show(321);</script><noscript><a target="_blank" href="http://ads.thehiveworks.com/delivery/ck.php?n=dda9649"><img border="0" alt="" src="http://ads.thehiveworks.com/delivery/avw.php?zoneid=321&amp;n=dda9649"></a></noscript>
    </div>

## TODO ~*whoops*~ there's no way for the comic to express that it needs this present on the homepage
<link rel="stylesheet" type="text/css" href="${request.route_url('pyscss', css_path='comic')}">
## TODO lollll.  someday this will be a mildly configurable gizmo of some description...
${request.registry.spline_plugins['comic'].render(context, request, 'latest-page')}

</div>
<div class="front-page-sidebar">
    <div id="ibar"></div>
    <script src="http://www.thehiveworks.com/jumpbar.js"></script>

    <div style="display: flex; margin: 1em 0.5em;">
        ## the money box goes right here yep
        <div style="flex: 1; margin: 1em;">
            <img src="/static/images/home-hiveworks.png" style="width: 100%;">
            <br>
            <img src="/static/images/home-patreon.png" style="width: 100%;">
        </div>

        <div class="ad ad-160x600">
            <script>/* [id322] www.floraverse.com - tower */ OA_show(322);</script><noscript><a target="_blank" href="http://ads.thehiveworks.com/delivery/ck.php?n=dda9649"><img border="0" alt="" src="http://ads.thehiveworks.com/delivery/avw.php?zoneid=322&amp;n=dda9649"></a></noscript>
        </div>
    </div>
    <!--
    <section>
        <h1>my cool blog entry</h1>
    </section>
    -->
</div>
</main>
</%block>
