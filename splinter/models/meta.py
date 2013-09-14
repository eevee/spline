"""SQLAlchemy declarative metashenanigans."""

from sqlalchemy.ext.declarative import DeclarativeMeta


class DeferredTableProp(object):
    """Declarative property that needs to do some work on the entire table just
    before class construction time.  Generally used for writing column-like
    accessors that also add other table or mapper properties, e.g. constraints.

    `pre_create` will be called on your deferred object from within the
    declarative class's `__new__`.  You'll get a view of a
    partially-constructed table to do with as you please.

    `post_create` will be called on your deferred object after the class has
    been constructed, and will receive the class itself.
    """
    def pre_create(self, key, partial_class):
        # Keep ourselves in the class dict as usual by default
        return self

    def post_create(self, key, cls):
        pass


class PartialMappedClass(object):
    """A more helpful view of the class dict for a pending declarative class.
    """
    def __init__(self, attrs):
        table_args = attrs.get('__table_args__', ())
        if table_args and isinstance(table_args[-1], dict):
            self.table_args = table_args[:-1]
            self.table_kwargs = dict(table_args[-1])
        else:
            self.table_args = table_args
            self.table_kwargs = {}

        self.mapper_kwargs = attrs.get('__mapper_args__', {})

    def configure_table(self, *args, **kwargs):
        """Add more arguments to the `Table` constructor."""
        self.table_args += args
        self.table_kwargs.update(kwargs)

    def finish(self, attrs):
        """Inject any aggregate values (like table args) into the new class's
        attrs dict, just before it's created.
        """
        attrs['__table_args__'] = self.table_args + (self.table_kwargs,)
        attrs['__mapper_args__'] = self.mapper_kwargs


class SplinterDeclarativeMeta(DeclarativeMeta):
    """Declarative metaclass that recognizes and evaluates "deferred"
    properties.
    """

    # Parent uses __init__, but we need to edit the attrs
    def __new__(meta, name, bases, attrs):
        partial_class = PartialMappedClass(attrs)
        new_attrs = {}

        deferreds = []

        for key, value in attrs.items():
            if isinstance(value, DeferredTableProp):
                deferreds.append((key, value))
                new_attrs[key] = value.pre_create(key, partial_class)
            else:
                new_attrs[key] = value

        partial_class.finish(new_attrs)

        return DeclarativeMeta.__new__(meta, name, bases, new_attrs)

    def __init__(cls, name, bases, attrs):
        # Do this first since it actually assigns all the column names, etc
        DeclarativeMeta.__init__(cls, name, bases, attrs)

        # This is always safe to do, because the attrs passed here is the same
        # as the one passed to __new__ originally -- NOT the one actually used
        # to populate the class!
        for key, value in attrs.items():
            if isinstance(value, DeferredTableProp):
                value.post_create(key, cls)
