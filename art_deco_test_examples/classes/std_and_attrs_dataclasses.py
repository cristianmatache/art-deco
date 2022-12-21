from __future__ import annotations

import inspect
from dataclasses import dataclass as std_dataclass
from dataclasses import field
from typing import List

from attr import NOTHING, attrib
from attr import dataclass as attrs_dataclass

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs


@std_dataclass
class StdDataClass:
    a: int
    b: float = 3
    c: int = field(default=10)
    d: List[int] = field(default_factory=list)


@attrs_dataclass
class AttrsDataClass:
    a: int
    b: float = 3
    c: int = attrib(default=10)
    d: List[int] = attrib(factory=list, kw_only=True)


EXPECTED_STD_DATA_CLASS = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='a', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='b', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=float, default_val=3),
        StaticArgSpec(name='c', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=10),
        # d's default value should be of type <factory>, which we can't access
    ],
    sig=inspect.signature(StdDataClass),
)

EXPECTED_ATTRS_DATA_CLASS = StaticArgSpecs(
    args=[
        StaticArgSpec(
            name='a', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
        ),
        StaticArgSpec(name='b', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=float, default_val=3),
        StaticArgSpec(name='c', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=10),
        StaticArgSpec(name='d', kind=ArgKind.KEYWORD_ONLY, annotation=List[int], default_val=NOTHING),
    ],
    sig=inspect.signature(AttrsDataClass),
)
