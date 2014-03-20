from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Column
from sqlalchemy.types import TypeEngine
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode

from spline.routing import to_slug


def _make_column(explicit_args, explicit_kwargs, *default_args, **default_kwargs):
    """Helper for creating column helpers.  Combine the default args/kwargs
    with those passed in by the caller and return a Column object.
    """
    # kwargs are pretty easy
    kwargs = default_kwargs
    kwargs.update(explicit_kwargs)

    # args are a bit trickier; for now, only check whether a type was passed in
    if explicit_args and default_args:
        if isinstance(explicit_args[0], TypeEngine) and isinstance(default_args[0], TypeEngine):
            default_args = (explicit_args[0],) + default_args
            explicit_args = explicit_args[1:]

    args = default_args + explicit_args

    return Column(*args, **kwargs)


class DeferredAttribute(object):
    """Minor hackery used with `deferred_attr_factory`."""
    # Hopefully, more or less, self-explanatory.  The __call__ is triggered at
    # class creation time by declared_attr, which passes in the class itself,
    # and then we do the "post" setup by listening for mapper_configured.
    def __init__(self, generator):
        self.generator = generator
        self.done = False

    def __call__(self, mapped_class):
        attribute = next(self.generator)

        listen(mapped_class, "mapper_configured", self._on_mapper_configured)
        return attribute

    def _on_mapper_configured(self, mapper, mapped_class):
        # Only do this setup ONCE!  It's possible for mapper_configured to fire
        # more than once, in the face of egregious shenanigans.
        if self.done:
            return
        self.done = True

        # Run the rest of the generator and close it
        try:
            self.generator.send(mapped_class)
        except StopIteration:
            pass
        self.generator.close()


def deferred_attr_factory(f):
    """Wrap a function to produce "deferred" declarative attributes.  The
    wrapped function can provide a column (or whatever) to be added to some
    mapped class, but it can also do some further setup after the class is
    fully constructed.

    Because the two steps may happen some time apart, the wrapped function MUST
    be a generator, yielding the object it wants to "return" into the class
    body.  The generator will later be sent the entire class to do with as it
    pleases.

    This is most convenient when making custom column types, because you don't
    necessarily know the name of the column until after the class is created.
    For example:

        @deferred_attr_factory
        def make_some_kinda_column(*args):
            column = Column(*args)
            mapped_class = yield column
            print(column.key)

        class SomeTable(Base):
            foo = make_some_kinda_column(Integer)
            # At mapper config time, "foo" will be printed.  Magic!
    """

    def attribute(*args, **kwargs):
        # This happens when the "function" is called in the body of a
        # declarative class.  This is the factory part.
        return declared_attr(DeferredAttribute(f(*args, **kwargs)))

    return attribute


# And now, the actual column types.

def SurrogateKeyColumn(*args, **kwargs):
    return _make_column(
        args, kwargs,
        Integer,
        nullable=False,
        primary_key=True,
        autoincrement=True)


def TitleColumn(*args, **kwargs):
    return _make_column(
        args, kwargs,
        Unicode,
        nullable=False)


@deferred_attr_factory
def SlugColumn(title_column, *args, **kwargs):
    column = _make_column(args, kwargs, Unicode, nullable=False)

    mapped_class = yield column

    def set_slug(target, value, oldvalue, initiator):
        setattr(target, title_column.key, to_slug(value))

    title_attr = getattr(mapped_class, title_column.key)
    listen(title_attr, 'set', set_slug)
