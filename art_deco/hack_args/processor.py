from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from functools import partial
from typing import Any, Callable, Mapping, Type, TypeVar, Union, cast

from typing_extensions import TypeGuard

from art_deco.core.arg_processors.api import ArgName, ArgNames, Context, MultiArgValidateFunc
from art_deco.core.arg_processors.dynamic_decorator import dynamic_process_args
from art_deco.core.arg_processors.static_decorator import static_process_args
from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec
from art_deco.core.specs.static_arg_specs import StaticArgSpecs
from art_deco.core.specs.static_inspector import ParseTypeHints, get_static_arg_specs
from art_deco.core.specs.type_hints_parsers import ExtrasTypeHintsParser
from art_deco.hack_args.marks import Marks
from art_deco.utils.typing_utils import is_annotated

_F = TypeVar('_F', bound=Callable)
SingleArgHackFuncDirect = Callable[[Any], Any]  # The value is passed directly
SingleArgHackFuncWithSpec = Callable[[StaticArgSpecs, DynamicArgSpec], Any]  # Pass static specs and dynamic spec
SingleArgHackFunc = Union[SingleArgHackFuncWithSpec, SingleArgHackFuncDirect]
ExplicitHacks = Mapping[Union[ArgName, ArgNames], Union[SingleArgHackFunc, MultiArgValidateFunc]]


def hack_args(
    hacks: ExplicitHacks | None = None,
    *,
    parse_type_hints: ParseTypeHints = True,
    is_dynamic: bool = False,
) -> Callable[[_F], _F]:
    split_hacks = _SplitHacks.from_explicit_hacks(hacks)

    if is_dynamic:

        def decorator(func: _F) -> _F:
            return dynamic_process_args(  # pylint: disable=no-value-for-parameter  # false positive due to wrapt
                partial(dynamic_processor_factory, wrapped=func, split_hacks=split_hacks),
                parse_type_hints=parse_type_hints,
            )(func)

    else:

        def decorator(func: _F) -> _F:  # noqa: WPS440
            extras_static_specs = get_static_arg_specs(func, parse_type_hints=ExtrasTypeHintsParser)
            return static_process_args(
                partial(static_processor_factory, extras_static_specs=extras_static_specs, split_hacks=split_hacks),
                parse_type_hints=parse_type_hints,
            )(func)

    return decorator


@dataclass
class _SplitHacks:
    single_arg_hacks: Mapping[ArgName, SingleArgHackFunc]
    multi_arg_hacks: Mapping[ArgNames, MultiArgValidateFunc]

    @classmethod
    def from_explicit_hacks(cls: Type[_SplitHacks], hacks: ExplicitHacks | None) -> _SplitHacks:
        if hacks is None:
            return cls({}, {})
        single_arg_hacks: dict[ArgName, SingleArgHackFunc] = {}
        multi_arg_hacks: dict[ArgNames, MultiArgValidateFunc] = {}
        for key, value in hacks.items():
            if isinstance(key, str):
                single_arg_hacks[key] = cast(SingleArgHackFunc, value)
            else:
                multi_arg_hacks[key] = cast(MultiArgValidateFunc, value)
        return cls(single_arg_hacks, multi_arg_hacks)


def static_processor_factory(
    static_specs: StaticArgSpecs,
    extras_static_specs: StaticArgSpecs,
    split_hacks: _SplitHacks,
) -> HackArgProcessor:
    single_hacks, multi_checks = collect_hacks(extras_static_specs, split_hacks)
    return HackArgProcessor(static_specs, single_hacks, multi_checks)


def dynamic_processor_factory(
    context: Context,
    split_hacks: _SplitHacks,
    wrapped: _F,
) -> HackArgProcessor:
    extras_static_specs = get_static_arg_specs(wrapped, parse_type_hints=ExtrasTypeHintsParser)
    single_hacks, multi_checks = collect_hacks(extras_static_specs, split_hacks)
    return HackArgProcessor(context.static_args, single_hacks, multi_checks)


def collect_hacks(  # noqa: WPS231
    extras_static_specs: StaticArgSpecs,
    split_hacks: _SplitHacks,
) -> tuple[Mapping[ArgName, SingleArgHackFunc], Mapping[ArgNames, MultiArgValidateFunc]]:
    annotated_single_hacks: dict[ArgName, SingleArgHackFunc] = {}
    annotated_multi_hacks: defaultdict[MultiArgValidateFunc, list[ArgName]] = defaultdict(list)
    for arg in extras_static_specs.args:
        if not arg.has_annotation:
            continue
        hint = arg.annotation
        if is_annotated(hint) and hasattr(hint, '__metadata__'):  # noqa: WPS421
            for ann_arg in hint.__metadata__:
                if is_hack_arg_func(ann_arg):
                    annotated_single_hacks[arg.name] = ann_arg  # noqa: WPS220
                if is_hack_args_func(ann_arg):
                    annotated_multi_hacks[ann_arg].append(arg.name)  # noqa: WPS220
    annotated_multi_hacks_by_args = {tuple(value): key for key, value in annotated_multi_hacks.items()}
    single_hacks = {**annotated_single_hacks, **split_hacks.single_arg_hacks}
    multi_checks = {**annotated_multi_hacks_by_args, **split_hacks.multi_arg_hacks}
    return single_hacks, multi_checks


@dataclass
class HackArgProcessor:
    static_specs: StaticArgSpecs
    single_hacks: Mapping[ArgName, SingleArgHackFunc]
    multi_checks: Mapping[ArgNames, MultiArgValidateFunc]

    def process_arg(self, arg: DynamicArgSpec, _: Context) -> Any:
        func = self.single_hacks[arg.name]
        if is_hack_arg_without_specs(func):
            return func(arg.value)
        if is_hack_arg_with_specs(func):
            return func(self.static_specs, arg)
        raise ValueError(
            f'Need to mark hack function {func} for arg {arg} with a mark from the art_deco.hack_args.marks module'
        )

    def should_process_arg(self, arg: str) -> bool:
        return arg in self.single_hacks

    def get_wide_checks(self) -> Mapping[ArgNames, MultiArgValidateFunc]:
        return self.multi_checks


def is_hack_arg_func(func: Any) -> bool:
    if not callable(func):
        return False
    mark = Marks.single_arg
    return hasattr(func, mark)  # noqa: WPS421


def is_hack_args_func(func: Any) -> bool:
    if not callable(func):
        return False
    return hasattr(func, Marks.many_args)  # noqa: WPS421


def is_hack_arg_without_specs(func: Any) -> TypeGuard[SingleArgHackFuncDirect]:
    mark = Marks.single_arg
    return hasattr(func, mark) and not getattr(func, mark)  # noqa: WPS421


def is_hack_arg_with_specs(func: Any) -> TypeGuard[SingleArgHackFuncWithSpec]:
    mark = Marks.single_arg
    return hasattr(func, mark) and getattr(func, mark)  # noqa: WPS421
