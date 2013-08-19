<%inherit file="splinter:templates/_base.mako" />

<section>
    <h1>Upload</h1>

    <form action="" method="POST" enctype="multipart/form-data">
        <fieldset>
            <dl class="vertical">
                <dd><input type="file" name="file"></dd>

                <dd><button type="submit">Upload</button></dd>

            </dl>
        </fieldset>
    </form>
</section>

