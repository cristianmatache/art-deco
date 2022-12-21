from __future__ import annotations

import inspect
from typing import Callable


def _is_like_classmethod(func: Callable) -> bool:
    """A regular method defined on a metaclass behaves the same way as a method decorated with @classmethod defined on a
    regular class.

    This function covers both use cases.
    """
    is_method = inspect.ismethod(func)
    return is_method and isinstance(func.__self__, type)  # type: ignore[attr-defined]


def is_decorated_classmethod(func: Callable) -> bool:
    """Check if fn is a classmethod declared with the @classmethod decorator.

    Adapted from:
    https://stackoverflow.com/questions/19227724/check-if-a-function-uses-classmethod
    """
    if not _is_like_classmethod(func):
        return False
    bound_to = func.__self__  # type: ignore[attr-defined]
    assert isinstance(bound_to, type)
    name = func.__name__
    for cls in bound_to.__mro__:  # noqa: WPS117
        descriptor = vars(cls).get(name)  # noqa: WPS421
        if descriptor is not None:
            return isinstance(descriptor, classmethod)
    return False


def is_classmethod_from_meta(func: Callable) -> bool:
    """Check if fn is a regular method defined on a metaclass (which behaves like an @classmethod method defined on a
    regular class)."""
    return not is_decorated_classmethod(func) and _is_like_classmethod(func)


def get_callable_arg_names(func: Callable) -> list[str]:
    """Get argument names of a function.

    :param func: get argument names for this function.
    :returns: list of argument names to be matched with the positional args passed in the decorator.

    .. note::
       Excludes first positional "self" or "cls" arguments if needed:
           - exclude self:
               - if fn is a method (self being an implicit argument)
           - exclude cls:
               - if fn is a decorated classmethod in Python 3.9+
               - if fn is declared as a regular method on a metaclass

    For functions decorated with ``@classmethod``, cls is excluded only in Python 3.9+
    because that is when Python's handling of classmethods changed and wrapt mirrors it.

    See: https://github.com/GrahamDumpleton/wrapt/issues/182
    """
    arg_spec_args = list(inspect.signature(func).parameters)
    first_arg_is_self = arg_spec_args and arg_spec_args[0] == 'self'
    # Exclusion criteria
    is_regular_method = inspect.ismethod(func) and first_arg_is_self
    if is_regular_method:
        # Don't include "self" argument
        arg_spec_args = arg_spec_args[1:]
    return arg_spec_args
