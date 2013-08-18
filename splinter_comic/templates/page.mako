<%inherit file="splinter:templates/_base.mako" />

<style type="text/css">
    .comic-page {
        width: 800px;
        margin: 1em auto;
        text-align: center;
    }
    .comic-page-image {
        background: white;
        padding: 3px;
        border: 1px solid #606060;
        box-shadow: 0 1px 3px #808080;
    }
</style>

<section>
    <h1>My Sweet Comic</h1>
    
    <div class="comic-page">
        <div class="comic-page-controls">
            % if prev_page:
                <a href="${request.route_url('comic.page', id=prev_page.id)}">«</a>
            % else:
                «
            % endif

            ·

            % if next_page:
                <a href="${request.route_url('comic.page', id=next_page.id)}">»</a>
            % else:
                »
            % endif
        </div>
        <img src="${request.static_url('splinter:../data/filestore/' + page.file)}"
            class="comic-page-image">
    </div>
</section>
