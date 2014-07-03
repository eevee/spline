import types

from sqlalchemy.event import listen
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.schema import Column
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import mapper
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator
from sqlalchemy.types import TypeEngine
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode
from sqlalchemy.types import UnicodeText
from sqlalchemy.util import set_creation_order


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


def copy_creation_order(fromobj, toobj):
    """Copies the value set by `set_creation_order` from the first argument
    onto the second.
    """
    toobj._creation_order = fromobj._creation_order


def sort_ordered_props(props):
    """Sort an `OrderedProperties` (often used for a list of columns) by the
    properties' creation order.
    """
    props._data.sort(key=lambda k: props[k]._creation_order)


# TODO should this move out of here to a general-purpose sqla hacks module?
class DeferredAttribute(declared_attr):
    """Minor hackery used with `deferred_attr_factory`."""
    # Hopefully, more or less, self-explanatory.  The __get__ overrides the
    # usual behavior of declared_attr and is triggered during class creation
    # time.  We get the owning class from the descriptor protocol, find the key
    # we're assigned to by skimming the class dict, and then do post-creation
    # setup by adding a listener for just before the mapper is configured.
    def __init__(self, f, args, kwargs):
        self.f = f
        self.args = args
        self.kwargs = kwargs

        set_creation_order(self)

    def __get__(self, inst, owner):
        # Should only ever be called on the class, not an instance
        assert inst is None

        # TODO this is probably all wrong for mixins
        for key, value in owner.__dict__.items():
            if value is self:
                attribute_key = key
                break
        else:
            raise RuntimeError("Couldn't find myself in the class dict??")

        ret = self.f(attribute_key, *self.args, **self.kwargs)

        if isinstance(ret, types.GeneratorType):
            attribute = next(ret)

            # Save some stuff we'll need in the handler
            self.generator = ret
            self.mapped_class = owner

            # This event is fired just before anything is configured, which
            # makes it a good time to add new columns and properties
            listen(mapper, "before_configured", self.on_configure, once=True)
        else:
            attribute = ret

        # The returned attribute is replacing us, so it should assume our
        # creation order
        copy_creation_order(self, attribute)

        return attribute

    def on_configure(self):
        # Run the rest of the generator and close it
        try:
            self.generator.send(self.mapped_class)
        except StopIteration:
            pass
        else:
            raise RuntimeError(
                "A deferred_attr_factory generator should yield "
                "no more than once")

        self.generator.close()


def deferred_attr_factory(f):
    """Wrap a function to produce "deferred" declarative attributes.  The
    wrapped function can provide a column (or whatever) to be added to some
    mapped class, but it can also do some further setup after the class is
    fully constructed.

    Because the two steps may happen some time apart, the wrapped function may
    be a generator, yielding the object it wants to "return" into the class
    body.  The generator will later be sent the entire class to do with as it
    pleases.

    The wrapped function will be passed one extra initial argument: the name
    it's assigned to in the containing class.

    This is mostly useful for adding multiple things to a class, adding event
    listeners to attributes, or other setup that doesn't work while the class
    is being constructed and thus can't work with `declared_attr`.  Consider it
    a way to do `__declare_first__` or `last` without touching the class
    itself.  For example:

        @deferred_attr_factory
        def double_column(key, *args):
            column = Column(*args)
            mapped_class = yield column
            setattr(mapped_class, key + "2", Column(*args))

        class SomeTable(Base):
            foo = double_column(Integer)
            # Now we have two identical columns, foo and foo2.  Magic!
    """

    def attribute(*args, **kwargs):
        # This happens when the "function" is called in the body of a
        # declarative class.  This is the factory part.
        return DeferredAttribute(f, args, kwargs)

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


@deferred_attr_factory
def Relationship(key, remote_class, *args, **kwargs):
    remote_keys = class_mapper(remote_class).primary_key
    if len(remote_keys) > 1:
        raise ValueError("Can't (yet?) link to a table with a compound key")

    rel = relationship(
        remote_class,
        backref=kwargs.pop('backref', None),
    )
    mapped_class = yield rel

    # TODO split out relationship() kwargs
    column = _make_column(
        args, kwargs,
        ForeignKey(*remote_keys),
        primary_key=False,
        nullable=False,
    )

    setattr(mapped_class, key + '_id', column)

    # TODO i can't assign the column to the class at the correct time because
    # when we're called it's only halfway through being built  :(  so i have to
    # dig into some internals to make the column order /look like/ it would be
    # if the caller had specified the column manually.
    copy_creation_order(rel, column)
    sort_ordered_props(mapped_class.__table__.columns)
    sort_ordered_props(mapped_class.__table__.primary_key.columns)


def TitleColumn(*args, **kwargs):
    return _make_column(
        args, kwargs,
        Unicode,
        nullable=False)


@deferred_attr_factory
def SlugColumn(key, title_column, *args, **kwargs):
    # circular import otherwise
    from spline.routing import to_slug

    column = _make_column(args, kwargs, Unicode, nullable=False)

    mapped_class = yield column

    def set_slug(target, value, oldvalue, initiator):
        setattr(target, key, to_slug(value))

    title_attr = getattr(mapped_class, key)
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
