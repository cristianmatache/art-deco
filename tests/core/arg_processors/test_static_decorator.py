from __future__ import annotations

from typing import Any, Mapping, Type, cast
from unittest.mock import call, patch

from pytest import raises
from typing_extensions import Annotated

from art_deco.core.arg_processors.api import ArgNames, Context, MultiArgValidateFunc
from art_deco.core.arg_processors.static_decorator import static_process_args
from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec
from art_deco.core.specs.static_arg_specs import StaticArgSpecs
from art_deco.core.specs.type_hints_parsers import ExtrasTypeHintsParser
from art_deco.utils.typing_utils import is_annotated


class SimpleCastingProcessor:
    def __init__(self, static_args: StaticArgSpecs) -> None:
        self.static_args = static_args
        self.hacks: dict[str, Any] = {}
        for arg in static_args.args:
            if arg.has_annotation:
                self.hacks[arg.name] = arg.annotation

    def should_process_arg(self, arg: str) -> bool:
        return arg in self.hacks

    def process_arg(self, arg: DynamicArgSpec, _: Context) -> Any:
        return self.hacks[arg.name](arg.value)

    def get_wide_checks(self) -> Mapping[ArgNames, MultiArgValidateFunc]:
        return {}


def test_casting_processor() -> None:
    @static_process_args(SimpleCastingProcessor)
    def coercion(x: int, y: float) -> float:
        return x + y

    assert coercion('1', '2') == 3  # type: ignore[arg-type]  # mypy correctly identifies the error
    assert coercion('1', 2) == 3  # type: ignore[arg-type]  # mypy correctly identifies the error
    assert coercion(1, 2) == 3


class AnnotationBasedCastingProcessor:
    def __init__(self, static_args: StaticArgSpecs) -> None:
        self.static_args = static_args
        self.hacks: dict[str, Type] = {}
        for arg in static_args.args:
            if arg.has_annotation:
                hint = arg.annotation
                if (  # noqa: WPS337
                    is_annotated(hint)
                    and hasattr(hint, '__metadata__')  # noqa: WPS421
                    and hint.__metadata__[0] == 'art_deco.hack_args'
                ):
                    type_to_cast = hint.__metadata__[1]
                    self.hacks[arg.name] = type_to_cast

    def process_arg(self, arg: DynamicArgSpec, _: Context) -> Any:
        return self.hacks[arg.name](arg.value)

    def should_process_arg(self, arg: str) -> bool:
        return arg in self.hacks

    def get_wide_checks(self) -> Mapping[ArgNames, MultiArgValidateFunc]:
        return {}


def test_annotation_based_casting_processor() -> None:
    @static_process_args(AnnotationBasedCastingProcessor, parse_type_hints=ExtrasTypeHintsParser)
    def coerce_annotated(
        x: Annotated[Any, 'art_deco.hack_args', int], y: Annotated[Any, 'art_deco.hack_args', float], z: int
    ) -> float:
        return cast(float, x + y + z)

    assert coerce_annotated('1', '2', 10) == 13
    assert coerce_annotated('1', 2, 10) == 13
    assert coerce_annotated(1, 2, 10) == 13
    with raises(TypeError):
        assert coerce_annotated(1, 2, '10')  # type: ignore[arg-type]  # mypy identifies the error


def test_number_of_calls() -> None:
    with patch('tests.core.arg_processors.test_static_decorator.SimpleCastingProcessor') as processor:

        @static_process_args(processor)
        def coercion(x: int, y: float) -> float:
            return x + y

        coercion(1, 2)
        coercion(1, 2)
        coercion(1, 2)

        processor.assert_called_once()
        assert processor.return_value.should_process_arg.call_count == 2  # Only called once for each argument
        assert processor.return_value.should_process_arg.call_args_list == [call('x'), call('y')]
        assert processor.return_value.process_arg.call_count == 6  # Each call we are processing each arg
        assert processor.return_value.get_wide_checks.call_count == 3  # Called once for each call
