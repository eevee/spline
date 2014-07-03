<%inherit file="/_base.mako" />
<%namespace file="spline:templates/_lib.mako" name="lib" />

## TODO title might be nice here instead, but we have to parse the whole page
## to get it
<%block name="title">History for ${page.path}</%block>

<section>
    <h1>History for ${page.path}</h1>

    <table>
      <tbody>
      % for change in history:
        <tr>
            <td>${lib.timestamp(change.time)}</td>
            <td>
                % if change.author:
                ${lib.user(change.author)}
                % else:
                ${change.git_author.name} &lt;${change.git_author.email}&gt;
                % endif
            </td>
            <td>${change.message}</td>
        </tr>
      % endfor
      </tbody>
    </table>
</section>
