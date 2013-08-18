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
    
    % for page in pages:
    <div class="comic-page">
        <img src="${request.static_url('splinter:../data/filestore/' + page.file)}"
            class="comic-page-image">
    </div>
    % endfor
</section>
