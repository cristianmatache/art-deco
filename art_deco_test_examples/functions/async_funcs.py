from __future__ import annotations

import inspect

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs


async def async_func(x: int, *, y: float = 5) -> float:
    return x + y


ASYNC_FUNC = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='y', kind=ArgKind.KEYWORD_ONLY, annotation=float, default_val=5),
    ],
    sig=inspect.signature(async_func),
)
