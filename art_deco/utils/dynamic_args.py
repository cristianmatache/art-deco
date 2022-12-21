from __future__ import annotations

from dataclasses import asdict
from typing import Any, List, cast

from typing_extensions import TypedDict

from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpecs
from art_deco.utils.dictionary import select_keys


class DynamicSpecDict(TypedDict, total=True):
    name: str
    value: Any
    called_as_kw: bool


def dynamic_specs_to_dict(specs: DynamicArgSpecs) -> list[DynamicSpecDict]:
    res = [select_keys(asdict(arg), ['name', 'value', 'called_as_kw']) for arg in specs.args]
    return cast(List[DynamicSpecDict], res)
