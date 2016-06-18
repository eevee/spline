/*** markdown preview ***/
// TODO this should really be cleaned up and made part of spline core (CSS too!)
// TODO hey you know what would be great?  coffeescript.
// TODO this should fire onload too if the browser populates the textarea
$(function() {
    $('.js-markdown-preview').each(function() {
        var $preview = $('<div>', { 'class': 'js-markdown-preview--preview' });
        $(this).append($preview);
        var $el = $(this);
        var timer = null;
        var req = null;
        var render = function(markdown) {
            timer = null;
            req = $.ajax({
                url: '/api/render-markdown/',
                method: 'POST',
                data: {markdown: markdown},
                headers: { 'X-CSRF-Token': spline_csrf_token },
            });

            req.done(function(resp) {
                timer = null;
                req = null;
                $preview.html(resp.markup);
                // TODO try to scroll to show the same part
                // of the text the user is typing in
            });
            // TODO uhh failure
        };
        $(this).find('textarea').on('keypress', function(ev) {
            var $textarea = $(this);
            if (timer || req) {
                return;
            }
            timer = setTimeout(function() { render($textarea.val()); }, 1000);
        });
    });
});
