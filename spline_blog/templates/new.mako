<%!
    import spline.format as libfmt
    from spline.display.rendering import render_json as j
%>
<%inherit file="/_base.mako" />
<%namespace name="lib" file="/_lib.mako" />

<section>
    <%lib:form action="">
    <fieldset>
        <p>Title: <input type="text" name="title" length="50"></p>
        <script src="//cdn.ckeditor.com/4.5.4/standard-all/ckeditor.js"></script>
        <script>
            $(function() {
                CKEDITOR.on('instanceReady', function(evt) {
                    evt.editor.on('fileUploadRequest', function(evt) {
                        evt.data.fileLoader.xhr.setRequestHeader(
                            'X-CSRF-Token', ${request.session.get_csrf_token()|j});
                    });
                });
                $('textarea.ckeditor').each(function() {
                    CKEDITOR.replace(this, {
                        disableNativeSpellChecker: false,
                        entities: false,
                        entities_greek: false,
                        entities_latin: false,
                        extraPlugins: 'divarea,uploadimage',
                        // TODO or maybe just remove the toolbar button because i don't care
                        removePlugins: 'about,pastefromword,specialchar,scayt,table',
                        format_tags: 'p;h2;h3;h4;pre',
                        uploadUrl: ${request.route_url('blog.ckupload')|j}
                    });
                });
            });
        </script>
        <div>
            <textarea class="ckeditor" name="content"></textarea>
        </div>
        <footer><button type="submit">Post</button></footer>
    </fieldset>
    </%lib:form>
</section>
