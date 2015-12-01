<%inherit file="/_base.mako" />
<%namespace name="lib" file="/_lib.mako" />

## TODO title might be nice here instead, but we have to parse the whole page
## to get it
<%block name="title">Proposed changes to ${page.path}</%block>


<%!
    PYGIT2_ORIGIN_TO_CLASS = {
        ' ': 'git-diff-context',
        '+': 'git-diff-added',
        '-': 'git-diff-removed',
    }
%>

<style>
    .git-diff-context {
        background-color: #f4f4f4;
    }
    .git-diff-added {
        background-color: #e0f4e0;
    }
    .git-diff-removed {
        background-color: #f4e0e0;
    }
</style>

<section>
<h1>Proposed changes to ${page.path}</h1>
    % for branch_name, proposer, commits, diff in page.iter_branches('proposals/'):
    <section>
        ## TODO get user object outta this
        <h1><code>${branch_name}</code> via ${proposer}</h1>
        <%lib:form action="">
            <p>
                <input type="hidden" name="branch" value="${branch_name}">
                <button type="submit">approve</button>
            </p>
        </%lib:form>
        % for patch in diff:
            <h2><code>${patch.delta.new_file.path}</code></h2>
            % if patch.delta.new_file.path != patch.delta.old_file.path:
                <p>(moved from <code>${patch.delta.old_file.path}</code>)</p>
            % endif

            % for hunk in patch.hunks:
            ## TODO line numbers or something
            % for line in hunk.lines:
                <pre class="${PYGIT2_ORIGIN_TO_CLASS[line.origin]}">${line.content}</pre>
            % endfor
                ...
            % endfor
        % endfor
    </section>
    <hr>
    % endfor
</section>
