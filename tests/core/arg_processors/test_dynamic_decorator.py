from __future__ import annotations

from typing import Any, Mapping
from unittest.mock import call, patch

from art_deco.core.arg_processors.api import ArgNames, Context, MultiArgValidateFunc
from art_deco.core.arg_processors.dynamic_decorator import dynamic_process_args
from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec


class StringProcessor:
    def __init__(self, context: Context) -> None:
        self.static_args = context.static_args
        self.hacks = {arg.name for arg in context.static_args.args if arg.has_annotation}

    def should_process_arg(self, arg: str) -> bool:
        return arg in self.hacks

    def process_arg(self, arg: DynamicArgSpec, _: Context) -> Any:
        return f'processed{arg.value}'

    def get_wide_checks(self) -> Mapping[ArgNames, MultiArgValidateFunc]:
        return {}


def test_casting_processor() -> None:
    @dynamic_process_args(StringProcessor)
    def stringy(x: str, y: str) -> str:
        return x + y

    assert stringy('1', '2') == 'processed1processed2'


def test_number_of_calls() -> None:
    with patch('tests.core.arg_processors.test_dynamic_decorator.StringProcessor') as processor:

        @dynamic_process_args(processor)
        def some_func(x: str, y: str) -> str:
            return x + y

        n_calls = 3
        for _ in range(n_calls):
            some_func('1', '2')

        assert processor.call_count == n_calls  # The processor is created every time the function is called
        assert processor.return_value.should_process_arg.call_count == n_calls * 2  # Call for each arg every func call
        assert processor.return_value.should_process_arg.call_args_list == [call('x'), call('y')] * 3  # noqa: WPS435
        assert processor.return_value.process_arg.call_count == n_calls * 2  # Each call we are processing each arg
        assert processor.return_value.get_wide_checks.call_count == n_calls  # Called once for each call
