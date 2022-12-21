from __future__ import annotations

from typing import Any

from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec, DynamicArgSpecs
from art_deco.core.specs.static_arg_specs import ArgKind, StaticArgSpecs


def get_dynamic_arg_specs(static_specs: StaticArgSpecs, args: tuple, kwargs: dict[str, Any]) -> DynamicArgSpecs:
    """Bind the static parameters to the values which each argument was called with."""
    # pylint: disable=too-many-locals
    # A Python function is called with arguments in the following order:
    # 1. non-variable positional arguments
    # 2. variable positional arguments
    # 3. non-variable keyword arguments
    # 4. variable keyword arguments

    # 1. Positional and non-variable arguments (i.e., args for which we have a name and a value to match positionally)
    named_positional_args = [  # Do not convert to set because this needs to be ordered
        arg for arg in static_specs.positionable_and_non_var if arg not in set(kwargs) | set(static_specs.variable_args)
    ]
    named_positional_values: dict[str, Any] = dict(zip(named_positional_args, args))
    # 2. Variable positional args -> bind the values to made-up names since we don't have individual names for them
    variable_positional_values = {
        f'__art_deco_auto_name__{i}': val for i, val in enumerate(args[len(named_positional_args) :])
    }
    # 4. Arguments that go in the variable keyword-only argument (e.g. **kwargs)
    variable_keyword_args = set(kwargs) - set(static_specs.args_by_name)
    # 5. Arguments that were not supplied (the default values are relied upon)
    args_using_defaults = set(static_specs.args_by_name) - (
        set(named_positional_values) | set(kwargs) | set(static_specs.variable_args)
    )
    positional_only_args_using_defaults = {
        arg.name: arg.default_val
        for arg in static_specs.args
        if arg.name in args_using_defaults and arg.kind is ArgKind.POSITIONAL_ONLY
    }
    args_using_default_to_call_as_kwargs = {
        arg.name: arg.default_val
        for arg in static_specs.args
        if arg.name in args_using_defaults and arg.name not in positional_only_args_using_defaults
    }

    # For named (i.e. non-variable) arguments -> Bind arguments with values
    dynamic_args: list[DynamicArgSpec] = []  # The order matters because we'll take the *args in order from this list
    static_spec_by_name = static_specs.args_by_name

    args_to_vals = {  # The order matters because based on this we are going to build the `dynamic_args`
        **named_positional_values,
        **positional_only_args_using_defaults,
        **variable_positional_values,
        **kwargs,
        **args_using_default_to_call_as_kwargs,
    }
    for arg_name, arg_val in args_to_vals.items():
        called_as_kw = arg_name in kwargs
        if arg_name in variable_keyword_args:
            # If the function has a **kwargs argument, and we have values for it -> bind those values to the same
            # static "kwargs" object
            assert static_specs.var_keyword is not None
            dynamic_arg = DynamicArgSpec(arg_name, arg_val, called_as_kw, static_specs.var_keyword)
        elif arg_name in variable_positional_values:
            # If the function has an *args argument, and we have values for it -> bind those values to the same
            # static "args" object
            assert static_specs.var_positional is not None
            dynamic_arg = DynamicArgSpec(arg_name, arg_val, called_as_kw, static_specs.var_positional)
        elif arg_name in args_using_default_to_call_as_kwargs:
            # If the argument is not supplied and we are using the default value -> mark it as called as kwarg
            # unless it is positional only (in which case this condition will not be met)
            dynamic_arg = DynamicArgSpec(arg_name, arg_val, called_as_kw=True, static=static_spec_by_name[arg_name])
        else:
            # Bind the value to the variable, by its name
            # (kwargs that are not specified in the signature will share the same static "kwargs" object but will have
            # separate names)
            dynamic_arg = DynamicArgSpec(arg_name, arg_val, called_as_kw, static_spec_by_name[arg_name])
        dynamic_args.append(dynamic_arg)
    return DynamicArgSpecs(dynamic_args)
