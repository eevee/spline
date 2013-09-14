from sqlalchemy.event import listen
from sqlalchemy.schema import Column
from sqlalchemy.types import TypeEngine
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode

from splinter.models.meta import DeferredTableProp
from splinter.routing import to_slug


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


class SlugColumn(DeferredTableProp):
    """Create a "slug" column automatically populated from another column's
    value.

    Note that the slug IS NOT updated when the other column is changed --
    presumably this column is being used in a URL, and implicitly changing URLs
    is super rude.
    """
    def __init__(self, title_column, *args, **kwargs):
        self.title_column = title_column
        self.args = args
        self.kwargs = kwargs

    def pre_create(self, key, partial_class):
        """Build a pretty typical text column to hold the slug."""
        return _make_column(
            self.args, self.kwargs,
            Unicode,
            nullable=False)

    def post_create(self, key, model_class):
        """Set an attribute listener on the class to update the slug when the
        title column is changed.
        """
        name_attr = getattr(model_class, self.title_column.key)

        def set_slug(target, value, oldvalue, initiator):
            setattr(target, key, to_slug(value))

        listen(name_attr, 'set', set_slug)
