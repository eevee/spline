from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Column
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import TypeEngine
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText


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


# TODO should this move out of here to a general-purpose sqla hacks module?
# would fit with extensions to, say, logging.  i need a cool word for that
# package.
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


def IdentifierColumn(*args, **kwargs):
    return _make_column(
        args, kwargs,
        UnicodeText,
        nullable=False,
        unique=True,
        index=True,
    )


def TitleColumn(*args, **kwargs):
    return _make_column(
        args, kwargs,
        Unicode,
        nullable=False)


@deferred_attr_factory
def SlugColumn(title_column, *args, **kwargs):
    # circular import otherwise
    from spline.routing import to_slug

    column = _make_column(args, kwargs, Unicode, nullable=False)

    mapped_class = yield column

    def set_slug(target, value, oldvalue, initiator):
        setattr(target, title_column.key, to_slug(value))

    title_attr = getattr(mapped_class, title_column.key)
    listen(title_attr, 'set', set_slug)


class Unrenderable(str):
    """String subclass which balks at being rendered directly into a template.
    Used for prose, which is a string, but which should very rarely be printed
    out directly.
    """
    # The rationale here is that it's very easy to print out trivial Markdown
    # (e.g. a single line of text) directly and think all is well and good,
    # then find out later that whoops no that was supposed to be rendered.
    def __html__(self):
        raise TypeError(
            "This string should never be treated as HTML!  "
            "Perhaps you meant to use render_prose?"
        )


class ProseType(TypeDecorator):
    # TODO there will almost certainly be a rendered-markdown cache somewhere
    # down the line; how on earth will that work with this setup?  use a type
    # that's a composite of the original and its cache?  or, uh, i guess it
    # depends on where the cache is stored.  hard to foresee from here.
    impl = Unicode

    def process_bind_param(self, value, dialect):
        # Python -> database.  Here we do nothing, because an AutoMarkdown is
        # already a string, which the db adapter should be able to handle just
        # fine.
        return value

    def process_result_value(self, value, dialect):
        # Database -> Python.  Wrap in an Unrenderable so the source can't be
        # accidentally rendered.
        return Unrenderable(value)


def ProseColumn(*args, **kwargs):
    return _make_column(
        args, kwargs,
        ProseType,
        nullable=False)
