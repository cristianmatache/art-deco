from __future__ import annotations

import inspect

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs


def simple_func(x):  # noqa: ANN001, ANN201 # Can be called with positional arg or keyword arg
    return x


def func_with_default(x, y=None):  # noqa: ANN001, ANN201
    resolved_y = 1 if y is None else y
    return x + resolved_y


SIMPLE_FUNC_STATIC_PARSE = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x',
            kind=ArgKind.POSITIONAL_OR_KEYWORD,
            annotation=Sentinels.NO_ANNOTATION,
            default_val=Sentinels.NO_DEFAULT_VALUE,
        )
    ],
    sig=inspect.signature(simple_func),
)

FUNC_WITH_DEFAULT_STATIC_PARSE = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x',
            kind=ArgKind.POSITIONAL_OR_KEYWORD,
            annotation=Sentinels.NO_ANNOTATION,
            default_val=Sentinels.NO_DEFAULT_VALUE,
        ),
        StaticArgSpec(
            name='y', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=Sentinels.NO_ANNOTATION, default_val=None
        ),
    ],
    sig=inspect.signature(func_with_default),
)

PARSED_SIMPLE_FUNCS = {  # noqa: WPS407
    simple_func: SIMPLE_FUNC_STATIC_PARSE,
    func_with_default: FUNC_WITH_DEFAULT_STATIC_PARSE,
}
