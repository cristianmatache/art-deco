from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from inspect import Signature
from typing import Any, Type


class Sentinels(Enum):
    NO_DEFAULT_VALUE = 1  # noqa: WPS115
    NO_ANNOTATION = 2  # noqa: WPS115

    def __repr__(self) -> str:
        return str(self)


class ArgKind(Enum):
    POSITIONAL_ONLY = 0  # noqa: WPS115
    POSITIONAL_OR_KEYWORD = 1  # noqa: WPS115
    VAR_POSITIONAL = 2  # noqa: WPS115
    KEYWORD_ONLY = 3  # noqa: WPS115
    VAR_KEYWORD = 4  # noqa: WPS115

    @classmethod
    def from_inspect(cls: Type[ArgKind], inspect_kind: Enum) -> ArgKind:
        return cls[inspect_kind.name]

    def __repr__(self) -> str:
        return str(self)


@dataclass(frozen=True)
class StaticArgSpec:
    name: str
    kind: ArgKind
    annotation: Any = Sentinels.NO_ANNOTATION
    default_val: Any = Sentinels.NO_DEFAULT_VALUE

    @property
    def has_default(self) -> bool:
        return self.default_val is not Sentinels.NO_DEFAULT_VALUE

    @property
    def has_annotation(self) -> bool:
        return self.annotation is not Sentinels.NO_ANNOTATION

    @property
    def is_variable(self) -> bool:
        return self.kind in {ArgKind.VAR_POSITIONAL, ArgKind.VAR_KEYWORD}

    @property
    def positionable_and_non_var(self) -> bool:
        return self.kind in {ArgKind.POSITIONAL_OR_KEYWORD, ArgKind.POSITIONAL_ONLY}


@dataclass(frozen=True)
class StaticArgSpecs:
    args: list[StaticArgSpec]
    sig: Signature  # This is to expose the internals, if anyone wants to use the built-in function result

    def __post_init__(self) -> None:
        if len(self._variable_positional_args) not in {0, 1}:
            raise AssertionError('Can take at most one variable positional param (e.g. *args)')
        if len(self._variable_positional_args) not in {0, 1}:
            raise AssertionError('Can take at most one variable keyword-only param (e.g. **kwargs)')

    @property
    def positionable_and_non_var(self) -> dict[str, StaticArgSpec]:
        """Args that may be called positionally but not as part of a variable positional arg."""
        return {arg.name: arg for arg in self.args if arg.positionable_and_non_var}

    @property
    def var_positional(self) -> StaticArgSpec | None:
        if not self._variable_positional_args:
            return None
        return self._variable_positional_args[0]

    @property
    def var_keyword(self) -> StaticArgSpec | None:
        if not self._variable_keyword_args:
            return None
        return self._variable_keyword_args[0]

    @property
    def variable_args(self) -> list[str]:
        return [arg.name for arg in self._variable_positional_args + self._variable_keyword_args]

    @property
    def args_by_name(self) -> dict[str, StaticArgSpec]:
        return {arg.name: arg for arg in self.args}

    @property
    def _variable_positional_args(self) -> list[StaticArgSpec]:
        return [arg for arg in self.args if arg.kind is ArgKind.VAR_POSITIONAL]

    @property
    def _variable_keyword_args(self) -> list[StaticArgSpec]:
        """Variable positional kwargs."""
        return [arg for arg in self.args if arg.kind is ArgKind.VAR_KEYWORD]
