import hashlib
import os.path
from pathlib import Path
import shutil

from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import Unicode
from zope.interface import Interface
from zope.interface import implementer


class FileManager(object):
    """Remembers configuration for various places and ways files can be
    stored, and helps store new files or manipulate existing ones.

    Files can be stored in a variety of backends (each being a `Storage`
    object), and are identified by faux URIs.  The manager's role is to let you
    not care about `Storage` objects at all, and merely convert a URI to a
    `File` object by whatever means are appropriate.

    Also the cool file browser in Windows 3.11.
    """

    def __init__(self):
        self.storages = []

    def add_storage(self, storage):
        self.storages.append(storage)


class IStorage(Interface):
    def store(fh, ext):
        """Store a file.  Arguments are an open file-like object and a file
        extension.
        """

    def get_url(filename, request):
        pass


class File(object):
    def __init__(self, storage, identifier):
        self.storage = storage
        self.identifier = identifier


@implementer(IStorage)
class FilesystemStorage(object):
    def __init__(self, directory):
        self.directory = Path(directory).resolve()

    def _dir_for(self, filename):
        if filename.startswith('tmp'):
            # BACKWARDS COMPAT
            # TODO remove
            return self.directory
        return self.directory / filename[0:3] / filename[3:6]

    # XXX INTERFACE NOT FINAL
    def store(self, fh, ext):
        """Store a file from a filehandle."""

        h = hashlib.sha256()
        fh.seek(0)
        while True:
            block = fh.read(8192)
            if not block:
                break
            h.update(block)

        filename = h.hexdigest() + ext

        fh.seek(0)
        parent_dir = self._dir_for(filename)
        if not parent_dir.isdir():
            parent_dir.mkdir(parents=True)
        path = parent_dir / filename

        with path.open('wb') as dest:
            shutil.copyfileobj(fh, dest)

        return filename

    def get_url(self, filename, request):
        # TODO this relies on stuff in app.py!
        return request.static_url(
            str(self._dir_for(filename) / filename))


class FileReference(object):
    def __init__(self, identifier):
        self.identifier = identifier

    def url_from_request(self, request):
        storage = request.registry.queryUtility(IStorage)
        return storage.get_url(self.identifier, request)


class StoredFile(TypeDecorator):
    impl = Unicode

    def process_bind_param(self, value, dialect):
        # Python to database
        return value

    def process_result_value(self, value, dialect):
        # Database to Python
        return FileReference(value)


# TODO does this all live here?  is this even a good idea?  it's not exactly...
# transactional.  should it write the file only on tpc_vote or something???
import transaction
from transaction.interfaces import IDataManager
from zope.interface import implementer

@implementer(IDataManager)
class FileDataManager(object):
    def __init__(self, path, transaction_manager=transaction.manager):
        self.path = path
        self.transaction_manager = transaction_manager

    def abort(self, txn):
        os.unlink(self.path)

    def tpc_begin(self, txn):
        pass

    def commit(self, txn):
        pass

    def tpc_vote(self, txn):
        pass

    def tpc_finish(self, txn):
        pass

    def tpc_abort(self, txn):
        pass

    def sortKey():
        # Try to sort even laster than the SQLA plugin, because we can't fail
        # but it can.  It uses "~sqlalchemy:id", so...
        return "~~file:{:d}".format(id(self.path))
