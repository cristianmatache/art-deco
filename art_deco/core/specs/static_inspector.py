from __future__ import annotations

import inspect
from typing import Callable, Type, Union

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs
from art_deco.core.specs.type_hints_parsers import TypeHintsParser
from art_deco.utils.inspection_utils import get_callable_arg_names

ParseTypeHints = Union[bool, TypeHintsParser, Type[TypeHintsParser]]


def get_type_hints_parser(parse_type_hints: ParseTypeHints, func: Callable) -> TypeHintsParser:
    if isinstance(parse_type_hints, TypeHintsParser):
        return parse_type_hints
    if isinstance(parse_type_hints, type) and issubclass(parse_type_hints, TypeHintsParser):
        return parse_type_hints(func)
    return TypeHintsParser(func)


def get_static_arg_specs(func: Callable, *, parse_type_hints: ParseTypeHints) -> StaticArgSpecs:
    arg_names = get_callable_arg_names(func)  # Does not contain self if called as an instance method
    inspected_signature = inspect.signature(func)
    if parse_type_hints:
        type_hints = {arg_name: Sentinels.NO_ANNOTATION for arg_name in arg_names}
        type_hints = {**type_hints, **get_type_hints_parser(parse_type_hints, func).parse()}
    else:
        type_hints = {
            param_name: Sentinels.NO_ANNOTATION if param.annotation is inspected_signature.empty else param.annotation
            for param_name, param in inspected_signature.parameters.items()
        }
    assert set(arg_names).issubset(type_hints)
    arg_specs = [
        StaticArgSpec(
            name=param_name,
            kind=ArgKind.from_inspect(param.kind),
            annotation=type_hints[param_name] if param_name in type_hints else Sentinels.NO_ANNOTATION,
            default_val=param.default if param.default is not inspected_signature.empty else Sentinels.NO_DEFAULT_VALUE,
        )
        for param_name, param in inspected_signature.parameters.items()
        if param_name in arg_names
    ]
    return StaticArgSpecs(arg_specs, inspected_signature)
