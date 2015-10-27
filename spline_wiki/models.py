from collections import namedtuple
from datetime import datetime

import pygit2
from pyramid.decorator import reify

# TODO this all cannot possibly work with distributed git.  the only way it
# could is to have a separate service in front of git that does all the db
# caching and whatnot.  something to consider?  (oops, this is exactly where i
# have the formatting problem)

WIKI_ENCODING = 'UTF-8'


def get_system_signature():
    # The timestamp is assigned when this is created, so we can't reuse the
    # same object forever
    return pygit2.Signature('System user', 'spline@localhost')


# TODO write an interface and use that to plug this into the registry
class Wiki(object):
    __name__ = None
    __parent__ = None

    def __init__(self, path):
        # TODO this should really be in some sort of first-install code.  or
        # app startup code.  wait, that's where it is now.
        # TODO assert somehow that the repo is writable by us?
        # TODO assert that it's EITHER empty OR a git repo, rather than dumping
        # git junk in an existing directory?
        self.repo = pygit2.init_repository(path, bare=True)
        if self.repo.is_empty:
            # Make a dummy empty commit to act as the HEAD
            treebuilder = self.repo.TreeBuilder()
            empty_tree = treebuilder.write()
            # HERE'S A GOOD QUESTION: what the fuck is the email here?
            # TODO if users have email addresses then we can use those...
            self.repo.create_commit(
                'refs/heads/master',
                get_system_signature(),
                get_system_signature(),
                u'Initial commit of an empty wiki',
                empty_tree,
                [],  # parents
            )

    def current_commit(self):
        return self.repo.head.get_object()

    def __getitem__(self, key):
        return WikiPage(self, (key,))

    def read(self, path):
        return u''

    def get_history(self):
        return self.repo.walk(
            self.current_commit().oid,
            pygit2.GIT_SORT_TOPOLOGICAL | pygit2.GIT_SORT_TIME,
        )


class WikiPage(object):
    __scope__ = 'wiki'

    def __init__(self, wiki, parts=()):
        self.wiki = wiki
        self.parts = parts

    # Pyramid Resource API
    @property
    def __name__(self):
        return self.parts[-1]

    @property
    def __parent__(self):
        if len(self.parts) > 1:
            return WikiPage(self.wiki, self.parts[:-1])
        else:
            return self.wiki

    def __getitem__(self, key):
        return WikiPage(self.wiki, self.parts + (key,))

    @property
    def path(self):
        return '/'.join(self.parts)

    @reify
    def git_path(self):
        if not self.parts:
            return ()
        return self.parts[:-1] + (self.parts[-1] + ".md",)

    @reify
    def tree_path_and_entry(self):
        tree = self.wiki.current_commit().tree
        trees = []
        for part in self.git_path:
            # Append is carefully done FIRST so we grab the root tree but not
            # the file tree, which is actually a tree entry
            trees.append(tree)

            if tree is not None and part in tree:
                tree_entry = tree[part]
                tree = self.wiki.repo[tree_entry.oid]
            else:
                tree_entry = None
                tree = None

        return trees, tree_entry

    @reify
    def tree_path(self):
        return self.tree_path_and_entry[0]

    @property
    def tree_entry(self):
        return self.tree_path_and_entry[1]

    @property
    def blob(self):
        return self.wiki.repo[self.tree_entry.oid]

    @reify
    def exists(self):
        return self.tree_entry is not None

    def read(self):
        # TODO wrap in Unrenderable
        return self.blob.data.decode('utf8')

    def write(self, new_data, author_name, author_email, message, *, branch='master'):
        assert self.path

        if branch is None:
            max_proposal_number = 0
            for existing_branch in self.wiki.repo.listall_branches():
                if existing_branch.startswith('proposals/'):
                    try:
                        max_proposal_number = max(max_proposal_number, int(existing_branch[10:]))
                    except ValueError:
                        pass

            branch = "proposals/{}".format(max_proposal_number + 1)

        # Create the file blob first
        blob_oid = self.wiki.repo.create_blob(new_data.encode(WIKI_ENCODING))
        new_tree_oid = None

        # Need to rebuild the tree from the bottom up.  Normally you'd do this
        # with an Index, which is considerably easier and understands paths and
        # all that, but this is a bare repo so there IS no index.
        # TODO actually i don't think that's true!
        for old_tree, name in reversed(list(zip(self.tree_path, self.git_path))):
            if old_tree is None:
                tb = self.wiki.repo.TreeBuilder()
            else:
                tb = self.wiki.repo.TreeBuilder(old_tree)

            if new_tree_oid is None:
                # First iteration: the entry is the file itself
                tb.insert(name, blob_oid, pygit2.GIT_FILEMODE_BLOB)
            else:
                # Add the last tree as a new entry
                tb.insert(name, new_tree_oid, pygit2.GIT_FILEMODE_TREE)
            new_tree_oid = tb.write()

        # Now commit it
        # TODO fix this to avoid the race condition when updating HEAD
        author = pygit2.Signature(author_name, author_email)
        self.wiki.repo.create_commit(
            'refs/heads/' + branch,
            author,
            get_system_signature(),  # helps distinguish web commits from not
            message,
            new_tree_oid,
            [self.wiki.current_commit().oid],
        )

    def iter_branches(self, prefix=''):
        for branch_name in self.wiki.repo.listall_branches():
            if not branch_name.startswith(prefix):
                continue

            head = self.wiki.repo.lookup_reference('refs/heads/' + branch_name)
            # TODO actually need to walk all commits not on master, but I'm not
            # entirely sure how to do that atm
            commit = head.peel()

            walker = self.wiki.repo.walk(commit.id, pygit2.GIT_SORT_TOPOLOGICAL)
            walker.hide(self.wiki.repo.head.peel().id)
            commits = list(walker)

            # TODO should check that we're touched anywhere in any of the
            # commits...
            tree = commit.tree
            for part in self.git_path:
                if part not in tree:
                    continue
                tree = self.wiki.repo[tree[part].id]

            # If we got here, we exist in this commit
            # TODO we really want to yield, like, the user and the message...
            # but there could be multiple commits so...  where does that all
            # go...  also there's no comment mechanism at the moment here
            # whoops
            yield branch_name, commit.author.email, commits, self.wiki.repo.diff(self.wiki.repo.head.peel().tree, commit.tree)

    def get_history(self):
        # TODO this needs a billion things.  limiting + pagination, looking up
        # users...  well maybe that's it actually
        path = '/'.join(self.git_path)  # TODO ugh christ
        history = WikiHistory()
        for commit in self.wiki.get_history():
            if path in commit.tree:
                history.add_commit(commit)

        return history


WikiChange = namedtuple('WikiChange', ('time', 'author', 'git_author', 'committer', 'git_committer', 'message'))


class WikiHistory:
    def __init__(self):
        self.commits = []
        self.all_emails = set()
        self.native_email_map = {}

    def add_commit(self, commit):
        self.commits.append(commit)
        self.all_emails.add(commit.author.email)
        self.all_emails.add(commit.committer.email)

    def __iter__(self):
        for commit in self.commits:
            yield WikiChange(
                time=datetime.utcfromtimestamp(commit.commit_time),
                author=self.native_email_map.get(commit.author.email),
                git_author=commit.author,
                committer=self.native_email_map.get(commit.committer.email),
                git_committer=commit.committer,
                message=commit.message,
            )
