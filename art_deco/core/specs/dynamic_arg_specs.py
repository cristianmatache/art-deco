from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from art_deco.core.specs.static_arg_specs import ArgKind, StaticArgSpec

_T = TypeVar('_T')


@dataclass(frozen=False)
class DynamicArgSpec(Generic[_T]):
    name: str
    value: _T
    called_as_kw: bool
    static: StaticArgSpec

    @property
    def is_default(self) -> bool:
        return self.value is self.static.default_val


@dataclass(frozen=True)
class DynamicVarArgSpec:
    combined_arg: DynamicArgSpec
    components: list[DynamicArgSpec]


@dataclass(frozen=True)
class DynamicArgSpecs:
    args: list[DynamicArgSpec]

    @property
    def args_by_name(self) -> dict[str, DynamicArgSpec]:
        return {arg.name: arg for arg in self.args}

    @property
    def args_called_as_kw(self) -> list[str]:
        return [arg.name for arg in self.args if arg.called_as_kw]

    @property
    def var_args_spec(self) -> DynamicVarArgSpec | None:
        args = [arg for arg in self.args if arg.static.kind is ArgKind.VAR_POSITIONAL]
        if not args:
            return None
        static_arg_names = list({arg.static.name for arg in args})
        assert len(static_arg_names) == 1
        combined_spec = DynamicArgSpec(
            name=static_arg_names[0],
            value=tuple(arg.value for arg in args),
            called_as_kw=False,
            static=args[0].static,
        )
        return DynamicVarArgSpec(combined_spec, args)

    @property
    def var_kwargs_spec(self) -> DynamicVarArgSpec | None:
        args = [arg for arg in self.args if arg.static.kind is ArgKind.VAR_KEYWORD]
        if not args:
            return None
        static_arg_names = list({arg.static.name for arg in args})
        assert len(static_arg_names) == 1
        combined_spec = DynamicArgSpec(
            name=static_arg_names[0],
            value={arg.name: arg.value for arg in args},
            called_as_kw=True,
            static=args[0].static,
        )
        return DynamicVarArgSpec(combined_spec, args)
