from __future__ import annotations

import inspect
from typing import Union

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs


def func_annotated_old_style(x: int, y: Union[str, float] = '1') -> float:
    return x + float(y)


def func_annotated_new_style(x: int, y: str | float = '1') -> float:
    return x + float(y)


FUNC_ANNOTATED_OLD_STYLE_PARSED_STATIC = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='y', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=Union[str, float], default_val='1'),
    ],
    sig=inspect.signature(func_annotated_old_style),
)

FUNC_ANNOTATED_OLD_STYLE_RAW_STATIC = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='int', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='y', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='Union[str, float]', default_val='1'),
    ],
    sig=inspect.signature(func_annotated_old_style),
)

FUNC_ANNOTATED_NEW_STYLE_RAW_STATIC = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='int', default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='y', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation='str | float', default_val='1'),
    ],
    sig=inspect.signature(func_annotated_new_style),
)


PARSED_ANNOTATED_FUNCS = {  # noqa: WPS407
    func_annotated_old_style: {
        True: FUNC_ANNOTATED_OLD_STYLE_PARSED_STATIC,
        False: FUNC_ANNOTATED_OLD_STYLE_RAW_STATIC,
    },
    func_annotated_new_style: {
        False: FUNC_ANNOTATED_NEW_STYLE_RAW_STATIC,
    },
}
