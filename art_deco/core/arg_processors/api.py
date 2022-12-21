from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Tuple

from typing_extensions import Protocol, runtime_checkable

from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec, DynamicArgSpecs
from art_deco.core.specs.static_arg_specs import StaticArgSpecs


@dataclass
class Context:
    static_args: StaticArgSpecs
    dynamic_args: DynamicArgSpecs


ArgName = str
ArgNames = Tuple[str, ...]
MultiArgValidateFunc = Callable[..., None]


@runtime_checkable
class ArgsProcessor(Protocol):
    def should_process_arg(self, arg: ArgName) -> bool:  # pylint: disable=unused-argument  # py 3.10+
        ...  # noqa: WPS428  # pragma: no cover

    def process_arg(self, arg: DynamicArgSpec, context: Context) -> Any:  # pylint: disable=unused-argument  # py 3.10+
        ...  # noqa: WPS428  # pragma: no cover

    def get_wide_checks(self) -> Mapping[ArgNames, MultiArgValidateFunc]:
        ...  # noqa: WPS428  # pragma: no cover
