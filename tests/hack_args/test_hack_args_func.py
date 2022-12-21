# flake8: noqa
from __future__ import annotations

import inspect
import sys
from asyncio import run
from typing import Type

from pytest import mark, raises
from typing_extensions import Annotated

from art_deco.core.arg_processors.api import Context
from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec
from art_deco.core.specs.static_arg_specs import StaticArgSpecs
from art_deco.hack_args.marks import arg_hacker, arg_hacker_with_specs, wide_validator
from art_deco.hack_args.processor import hack_args
from art_deco_test_examples.functions.async_funcs import async_func


@arg_hacker
def hack_x(x: float | str) -> float:
    if isinstance(x, str):
        return 10
    return x


@arg_hacker_with_specs
def hack_y(specs: StaticArgSpecs, spec: DynamicArgSpec[float]) -> float:
    assert isinstance(specs, StaticArgSpecs)
    if spec.static.default_val == 3:
        return 20
    return spec.value


@arg_hacker_with_specs
def hack_z(specs: StaticArgSpecs, spec: DynamicArgSpec[int]) -> float:
    assert isinstance(specs, StaticArgSpecs)
    if spec.static.annotation == int:
        return 30
    return spec.value


@wide_validator
def validate_x_z(_: Context, x: float, z: float) -> None:
    assert x + z < 10**5


@mark.parametrize('is_dynamic', [False, True])
def test_hack_args_func(is_dynamic: bool) -> None:
    @hack_args({'x': hack_x, 'y': hack_y, ('x', 'z'): validate_x_z}, is_dynamic=is_dynamic)
    def add(x: float, y: int = 3, z: Annotated[int, hack_z] = 4) -> float:
        return x + y + z

    assert add('a', 2, 3) == 60  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert add(1) == 51


@mark.parametrize('is_dynamic', [False, True])
def test_hack_args_methods(is_dynamic: bool) -> None:
    class Example:
        @hack_args({'x': hack_x, 'y': hack_y, ('x', 'z'): validate_x_z}, is_dynamic=is_dynamic)
        # Note that hack_y takes priority
        def add_method(self, x: float, y: Annotated[int, hack_x] = 3, z: Annotated[int, hack_z] = 4) -> float:
            return x + y + z

        @staticmethod
        @hack_args(is_dynamic=is_dynamic)
        def add_static(
            x: Annotated[float, hack_x, validate_x_z],
            y: Annotated[int, hack_y] = 3,
            z: Annotated[int, hack_z, 'something', validate_x_z, 'some other thing'] = 4,
        ) -> float:
            return x + y + z

        @classmethod
        @hack_args({'x': hack_x, 'y': hack_y, 'z': hack_z}, is_dynamic=is_dynamic)
        # hack_y will take priority over the annotated hacker func
        def add_cls(cls: Type, x: Annotated[float, hack_x], y: int = 3, z: int = 4) -> float:
            return x + y + z

    assert Example().add_method('a', 2, 3) == 60  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert Example().add_method(1) == 51
    assert Example.add_static('a', 2, 3) == 60  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert Example.add_static(1) == 51
    assert Example.add_cls('a', 2, 3) == 60  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert Example.add_cls(1) == 51


@mark.parametrize('is_dynamic', [False, True])
def test_hack_args_coroutines(is_dynamic: bool) -> None:
    hacked_coroutine = hack_args({'x': hack_x}, is_dynamic=is_dynamic)(
        async_func
    )  # pylint: disable=no-value-for-parameter
    assert run(hacked_coroutine('a')) == 15  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert run(hacked_coroutine(1)) == 6
    assert run(hacked_coroutine(1, y=6)) == 7


@mark.parametrize('is_dynamic', [False, True])
def test_hack_args_async_methods(is_dynamic: bool) -> None:
    class ExampleAsync:
        @hack_args({'x': hack_x}, is_dynamic=is_dynamic)
        async def add_method(self, x: int, *, y: float = 5) -> float:
            return await async_func(x, y=y)

        @staticmethod
        @hack_args({'x': hack_x}, is_dynamic=is_dynamic)
        async def add_static(x: int, *, y: float = 5) -> float:
            return await async_func(x, y=y)

        @classmethod
        @hack_args(is_dynamic=is_dynamic)
        async def add_cls(cls: Type, x: Annotated[int, hack_x], *, y: float = 5) -> float:
            return await async_func(x, y=y)

    assert run(ExampleAsync().add_method('a')) == 15  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert run(ExampleAsync().add_method(1)) == 6
    assert run(ExampleAsync().add_method(1, y=6)) == 7

    assert run(ExampleAsync.add_static('a')) == 15  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert run(ExampleAsync.add_static(1)) == 6
    assert run(ExampleAsync.add_static(1, y=6)) == 7

    assert run(ExampleAsync.add_cls('a')) == 15  # type: ignore[arg-type]  # mypy correctly identifies the problem
    assert run(ExampleAsync.add_cls(1)) == 6
    assert run(ExampleAsync.add_cls(1, y=6)) == 7


@mark.parametrize('is_dynamic', [False, True])
def test_hack_args_default_arg(is_dynamic: bool) -> None:
    @hack_args({'x': hack_x, 'y': hack_y}, is_dynamic=is_dynamic)
    def add(x: float, y: int = 3) -> float:
        return x + y

    assert add(1) == 21


@mark.parametrize('is_dynamic', [False, True])
def test_no_annotation(is_dynamic: bool) -> None:
    @hack_args({'x': hack_x, 'y': hack_y}, is_dynamic=is_dynamic)
    def add(x, y=3):  # noqa: ANN201 # testing no annotations
        return x + y

    assert add(1) == 21


@mark.parametrize('is_dynamic', [False, True])
def test_unknown_func(is_dynamic: bool) -> None:
    def hack_x2(x: float | str) -> float:
        return hack_x(x)

    @hack_args({'x': hack_x2}, is_dynamic=is_dynamic)
    def add(x: float, y: int = 3) -> float:
        return x + y

    with raises(ValueError):
        assert add(1) == 21


@mark.skipif(sys.version_info[:2] >= (3, 9), reason='Forward references work in these python version')
def test_forward_references_error() -> None:
    with raises(NameError):

        class ExampleErr:  # pylint: disable=unused-variable
            @classmethod
            @hack_args(is_dynamic=False)
            def add_cls(cls: Type[ExampleErr]) -> ExampleErr:  # pylint: disable=undefined-variable
                return cls()


def test_forward_references_success() -> None:
    class ExampleSucc:  # pylint: disable=unused-variable
        @classmethod
        @hack_args(is_dynamic=True)
        def add_cls(cls: Type[ExampleSucc]) -> ExampleSucc:  # pylint: disable=undefined-variable
            return cls()


@arg_hacker_with_specs
def hack_var_args(_: StaticArgSpecs, args: DynamicArgSpec[tuple[float, ...]]) -> tuple[str, ...]:
    return tuple(f'args{val};' for val in args.value)


@arg_hacker
def hack_var_kwargs(kwargs: dict[str, int]) -> dict[str, str]:
    return {key: f'kwargs{value}' for key, value in kwargs.items()}


@arg_hacker
def hack_arg_by_name(arg: str) -> str:
    return f'hack{arg}'


@mark.parametrize('is_dynamic', [False, True])
def test_args_and_kwargs(is_dynamic: bool) -> None:
    if is_dynamic:
        # t is processed one more time when is_dynamic version because t is known at runtime but not at "compile" time
        expected = "x=1;y=hack5;args=('args2;', 'args3;', 'args4;');kwargs={'z': 'kwargs6', 't': 'hackkwargs7'}"
    else:
        expected = "x=1;y=hack5;args=('args2;', 'args3;', 'args4;');kwargs={'z': 'kwargs6', 't': 'kwargs7'}"

    @hack_args({'t': hack_arg_by_name}, is_dynamic=is_dynamic)  # t belongs to kwargs so it cannot be Annotated
    def add1(
        x: str,
        *args: Annotated[str, hack_var_args],
        y: Annotated[str, hack_arg_by_name],
        **kwargs: Annotated[str, hack_var_kwargs],
    ) -> str:
        return f'x={x};y={y};args={args};kwargs={kwargs}'

    assert expected == add1(1, 2, 3, 4, y=5, z=6, t=7)  # type: ignore # mypy correctly flags this

    @hack_args(
        {'args': hack_var_args, 'kwargs': hack_var_kwargs, 'y': hack_arg_by_name, 't': hack_arg_by_name},
        is_dynamic=is_dynamic,
    )
    def add2(x: int, *args: str, y: str, **kwargs: str) -> str:
        assert isinstance(x, int)
        return f'x={x};y={y};args={args};kwargs={kwargs}'

    assert expected == add2(1, 2, 3, 4, y=5, z=6, t=7)  # type: ignore # mypy correctly flags this
    # Not supplying t at all should be ignored whether is_dynamic or not
    res = add2(1, 2, 3, 4, y=5, z=6)  # type: ignore # mypy correctly flags this
    assert res == "x=1;y=hack5;args=('args2;', 'args3;', 'args4;');kwargs={'z': 'kwargs6'}"


def test_preserve_func_properties() -> None:
    @hack_args()
    def some_function(x: int) -> int:
        """Test docstring."""
        return x

    assert some_function.__doc__ == 'Test docstring.'
    sig = inspect.signature(some_function)
    assert len(sig.parameters) == 1
    assert sig.parameters['x'].annotation == 'int'
    assert sig.return_annotation == 'int'


def test_func_no_args() -> None:
    @hack_args({'x': hack_x})
    def no_args() -> None:
        return

    assert no_args() is None
