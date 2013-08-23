from sqlalchemy.schema import Column
from sqlalchemy.types import TypeEngine
from sqlalchemy.types import Integer
from sqlalchemy.types import Unicode

from splinter.routing import to_slug


def make_slug(column):
    """Automatically generates a slug from another column on INSERT or UPDATE.  Use like so:

        title = Column(Unicode, ...)
        title_slug = Column(Unicode, default=make_slug(title), onupdate=make_slug(title))

    Of course, you can also just do this:

        title = TitleColumn()
        title_slug = SlugColumn(title)
    """
    def impl(context):
        return to_slug(context.current_parameters[column.name])
    return impl


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


def SlugColumn(title_column, *args, **kwargs):
    return _make_column(
        args, kwargs,
        Unicode,
        nullable=False,
        default=make_slug(title_column),
        onupdate=make_slug(title_column))
