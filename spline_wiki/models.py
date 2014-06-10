import pygit2
from pyramid.decorator import reify

# TODO this all cannot possibly work with distributed git.  the only way it
# could is to have a separate service in front of git that does all the db
# caching and whatnot.  something to consider?  (oops, this is exactly where i
# have the formatting problem)

WIKI_ENCODING = 'UTF-8'


# TODO write an interface and use that to plug this into the registry
class Wiki(object):
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
            author = pygit2.Signature('spline_wiki', 'spline@localhost')
            self.repo.create_commit(
                'refs/heads/master',
                author, author,
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


class WikiPage(object):
    def __init__(self, wiki, parts=()):
        self.wiki = wiki
        self.parts = parts

    # Pyramid Resource API
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

    def write(self, new_data, author_name, author_email, message):
        assert self.path

        # Need to rebuild the tree from the bottom up.  Normally you'd do this
        # with an Index, which is considerably easier and understands paths and
        # all that, but this is a bare repo so there IS no index.
        tree_path_up = list(reversed(self.tree_path))

        # Create the file blob first, of course.
        blob_oid = self.wiki.repo.create_blob(new_data.encode(WIKI_ENCODING))
        new_tree_oid = None

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
        committer = pygit2.Signature('spline_wiki', 'spline@localhost')
        self.wiki.repo.create_commit(
            'refs/heads/master',
            author,
            committer,  # helps distinguish web commits from not
            message,
            new_tree_oid,
            [self.wiki.current_commit().oid],
        )
