from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

import wrapt

from art_deco.core.arg_processors.api import ArgName, ArgsProcessor, Context
from art_deco.core.arg_processors.processing import process
from art_deco.core.specs.dynamic_inspector import get_dynamic_arg_specs
from art_deco.core.specs.static_arg_specs import StaticArgSpecs
from art_deco.core.specs.static_inspector import ParseTypeHints, get_static_arg_specs

_F = TypeVar('_F', bound=Callable)


def static_process_args(
    processor_factory: Callable[[StaticArgSpecs], ArgsProcessor], *, parse_type_hints: ParseTypeHints = True
) -> Callable[[_F], _F]:
    def decorator(wrapped: _F) -> _F:
        static_specs = get_static_arg_specs(wrapped, parse_type_hints=parse_type_hints)
        processor = processor_factory(static_specs)
        assert isinstance(processor, ArgsProcessor)
        args_to_process = {arg_name for arg_name in static_specs.args_by_name if processor.should_process_arg(arg_name)}

        @wrapt.decorator
        def wrapper(  # pylint: disable=too-many-locals
            func: _F,
            instance: Any | None,
            args: tuple[Any, ...],
            kwargs: dict[str, Any],
        ) -> _F:
            args = (instance, *args) if instance is not None else args
            dynamic_specs = get_dynamic_arg_specs(static_specs, args, kwargs)
            new_args, new_kwargs = _process(processor, Context(static_specs, dynamic_specs), args_to_process)
            new_args = new_args[1:] if instance is not None else new_args
            return cast(_F, func(*new_args, **new_kwargs))

        return cast(_F, wrapper(wrapped))  # pylint: disable=no-value-for-parameter

    return decorator


def _process(
    processor: ArgsProcessor,
    context: Context,
    args_to_process: set[ArgName],
) -> tuple[list, dict[str, Any]]:
    return process(processor, context, lambda arg: arg in args_to_process)
