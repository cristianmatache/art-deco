from __future__ import annotations

import inspect
from typing import List, Optional

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs


def func_with_kwonly(x: int, y: float, *, z: float) -> float:
    return x + y + z


def func_with_var_args_and_kwargs(  # pylint: disable=keyword-arg-before-vararg  # pylint false positive
    x: int, y: List[float], z: str, t: Optional[str] = None, *args: int, some_keyword: float, **kwargs: float
) -> float:
    resolved_t = 100 if t is None else float(t)
    return x + sum(y) + float(z) + resolved_t + sum(args) + some_keyword + sum(kwargs.values())  # type: ignore


FUNC_WITH_KWONLY = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='y', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=float, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='z', kind=ArgKind.KEYWORD_ONLY, annotation=float, default_val=Sentinels.NO_DEFAULT_VALUE),
    ],
    sig=inspect.signature(func_with_kwonly),
)

VAR_ARGS_FUNC_PARSED = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='y', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=List[float], default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='z', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=str, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='t', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=Optional[str], default_val=None),
        StaticArgSpec(name='args', kind=ArgKind.VAR_POSITIONAL, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE),
        StaticArgSpec(
            name='some_keyword', kind=ArgKind.KEYWORD_ONLY, annotation=float, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='kwargs', kind=ArgKind.VAR_KEYWORD, annotation=float, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
    ],
    sig=inspect.signature(func_with_var_args_and_kwargs),
)

VAR_ARGS_FUNC_RAW = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='int', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='y',
            kind=ArgKind.POSITIONAL_OR_KEYWORD,
            annotation='List[float]',
            default_val=Sentinels.NO_DEFAULT_VALUE,
        ),
        StaticArgSpec(
            name='z', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='str', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='t', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='Optional[str]', default_val=None),
        StaticArgSpec(
            name='args', kind=ArgKind.VAR_POSITIONAL, annotation='int', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='some_keyword', kind=ArgKind.KEYWORD_ONLY, annotation='float', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(
            name='kwargs', kind=ArgKind.VAR_KEYWORD, annotation='float', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
    ],
    sig=inspect.signature(func_with_var_args_and_kwargs),
)

PARSED_VAR_ARG_FUNCS = {  # noqa: WPS407
    func_with_kwonly: {
        True: FUNC_WITH_KWONLY,
    },
    func_with_var_args_and_kwargs: {
        True: VAR_ARGS_FUNC_PARSED,
        False: VAR_ARGS_FUNC_RAW,
    },
}
