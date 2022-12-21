from __future__ import annotations

from typing import Any, Callable, TypeVar, cast

import wrapt

from art_deco.core.arg_processors.api import ArgsProcessor, Context
from art_deco.core.arg_processors.processing import process
from art_deco.core.specs.dynamic_inspector import get_dynamic_arg_specs
from art_deco.core.specs.static_inspector import ParseTypeHints, get_static_arg_specs

_F = TypeVar('_F', bound=Callable)


def dynamic_process_args(
    processor_factory: Callable[[Context], ArgsProcessor], *, parse_type_hints: ParseTypeHints = True
) -> Callable[[_F], _F]:
    @wrapt.decorator
    def wrapper(  # pylint: disable=too-many-locals
        func: _F,
        instance: Any | None,  # pylint: disable=unused-argument
        args: tuple[Any, ...],
        kwargs: dict[str, Any],
    ) -> _F:
        static_specs = get_static_arg_specs(func, parse_type_hints=parse_type_hints)
        dynamic_specs = get_dynamic_arg_specs(static_specs, args, kwargs)
        context = Context(static_specs, dynamic_specs)

        processor = processor_factory(context)
        assert isinstance(processor, ArgsProcessor)

        new_args, new_kwargs = _process(processor, context)
        return cast(_F, func(*new_args, **new_kwargs))

    return cast(Callable[[_F], _F], wrapper)


def _process(processor: ArgsProcessor, context: Context) -> tuple[list, dict[str, Any]]:
    return process(processor, context, processor.should_process_arg)
