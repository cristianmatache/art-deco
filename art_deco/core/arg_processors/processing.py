from __future__ import annotations

from typing import Any, Callable

from art_deco.core.arg_processors.api import ArgName, ArgsProcessor, Context


def process(  # pylint: disable=too-many-locals  # noqa: WPS231
    processor: ArgsProcessor,
    context: Context,
    should_process_arg: Callable[[str], bool],
) -> tuple[list, dict[str, Any]]:
    new_args: list = []
    new_kwargs: dict[ArgName, Any] = {}

    dynamic_specs = context.dynamic_args
    args_called_as_kw = dynamic_specs.args_called_as_kw

    # First pass: go through var args
    var_args_spec = dynamic_specs.var_args_spec
    if var_args_spec is not None and should_process_arg(var_args_spec.combined_arg.name):
        new_arg_values = processor.process_arg(var_args_spec.combined_arg, context)
        for component, new_val in zip(var_args_spec.components, new_arg_values):
            component.value = new_val
    var_kwargs_spec = dynamic_specs.var_kwargs_spec
    if var_kwargs_spec is not None and should_process_arg(var_kwargs_spec.combined_arg.name):
        new_kwargs_values = processor.process_arg(var_kwargs_spec.combined_arg, context)
        for component in var_kwargs_spec.components:  # noqa: WPS440
            component.value = new_kwargs_values[component.name]

    # Second pass: go through individual args
    for arg_name, spec in dynamic_specs.args_by_name.items():
        if should_process_arg(arg_name):
            spec.value = processor.process_arg(spec, context)

        # Rebuild args and kwargs
        if arg_name in args_called_as_kw:
            new_kwargs[arg_name] = spec.value
        else:
            new_args.append(spec.value)

    # Third pass: go through multi arg checks (i.e., "wide" validation checks across multiple args)
    new_arg_specs = dynamic_specs.args_by_name
    for multi_args, multi_arg_check in processor.get_wide_checks().items():
        multi_arg_check(context, *[new_arg_specs[name].value for name in multi_args])
    return new_args, new_kwargs
