from __future__ import annotations

from typing import Callable, TypeVar

_F = TypeVar('_F', bound=Callable)


class Marks:
    single_arg = '__art_deco__arg_hack_with_specs__'
    many_args = '__art_deco__args_hack__'


def arg_hacker(func: _F) -> _F:
    setattr(func, Marks.single_arg, False)
    return func


def arg_hacker_with_specs(func: _F) -> _F:
    setattr(func, Marks.single_arg, True)
    return func


def wide_validator(func: _F) -> _F:
    setattr(func, Marks.many_args, True)
    return func
