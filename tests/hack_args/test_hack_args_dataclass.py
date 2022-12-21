# flake8: noqa
from __future__ import annotations

from dataclasses import dataclass as std_dataclass
from typing import Any
from unittest.mock import patch

from attr import dataclass as attrs_dataclass
from pytest import mark
from typing_extensions import Annotated

from art_deco.core.arg_processors.api import Context
from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec
from art_deco.core.specs.static_arg_specs import StaticArgSpecs
from art_deco.hack_args.marks import arg_hacker, arg_hacker_with_specs, wide_validator
from art_deco.hack_args.processor import hack_args

try:
    from pydantic.dataclasses import dataclass as pydantic_dataclass
except ImportError:
    pydantic_dataclass = None  # type: ignore[assignment]


@arg_hacker
def hack_x(x: float | str) -> float:
    return 10 if isinstance(x, str) else x


@arg_hacker_with_specs
def hack_y(_: StaticArgSpecs, spec: DynamicArgSpec[float]) -> float:
    return 20 if spec.static.default_val == 3 else spec.value


@arg_hacker_with_specs
def hack_z(_: StaticArgSpecs, spec: DynamicArgSpec[int]) -> float:
    return 30 if spec.static.annotation == int else spec.value


@wide_validator
def validate_x_z(_: Context, x: float, z: float) -> None:
    assert x + z < 10**5


def get_dataclass_types() -> list:
    if pydantic_dataclass is not None:
        return [std_dataclass, attrs_dataclass, pydantic_dataclass]
    return [std_dataclass, attrs_dataclass]


@mark.parametrize('_dataclass', get_dataclass_types())
def test_hack_args_on_class(_dataclass: Any) -> None:
    @hack_args({'x': hack_x, 'y': hack_y, ('x', 'z'): validate_x_z})
    @_dataclass
    class ClassSimple:
        x: float
        y: int = 3
        z: int = 4

    @hack_args({'x': hack_x})
    @_dataclass
    class ClassMixAnn:
        x: Annotated[float, validate_x_z]
        y: Annotated[int, hack_y] = 3
        z: Annotated[int, hack_z, validate_x_z] = 4

    @hack_args({'x': hack_x})
    @_dataclass
    class ClassMixAnnPriority:
        x: Annotated[float, validate_x_z, hack_y]
        y: Annotated[int, hack_y] = 3
        z: Annotated[int, hack_z, validate_x_z] = 4

    @hack_args()
    @_dataclass
    class ClassAnn:
        x: Annotated[float, hack_x, validate_x_z]
        y: Annotated[int, hack_y] = 3
        z: Annotated[int, hack_z, validate_x_z] = 4

    assert ClassSimple('a', 100) == ClassSimple(x=10, y=20, z=4)  # type: ignore  # mypy sees the issue
    assert ClassMixAnn('a', 100) == ClassMixAnn(x=10, y=20, z=4)  # type: ignore  # mypy sees the issue
    assert ClassMixAnnPriority('a', 100) == ClassMixAnnPriority(x=10, y=20, z=4)  # type: ignore
    assert ClassAnn('a', 100) == ClassAnn(x='a', y=20, z=4)  # type: ignore  # mypy sees the issue

    with patch('tests.hack_args.test_hack_args_dataclass.validate_x_z') as valid_x_z:
        valid_x_z = wide_validator(valid_x_z)

        @hack_args()
        @_dataclass
        class ClassAnnCount:
            x: Annotated[float, hack_x, validate_x_z]
            y: Annotated[int, hack_y] = 3
            z: Annotated[int, hack_z, validate_x_z] = 4

        ClassAnnCount('a', 100)  # type: ignore  # mypy sees the issue
        valid_x_z.assert_called_once()


@hack_args({'x': hack_x, 'y': hack_y, ('x', 'z'): validate_x_z})
@std_dataclass
class SimpleClassForTyping:
    x: float
    y: int = 3
    z: int = 4


# reveal_type(SimpleClassForTyping)
# reveal_type(SimpleClassForTyping(x=1, y=2, z=4))
