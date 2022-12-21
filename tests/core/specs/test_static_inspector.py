import inspect
import sys
from typing import Callable, List, Optional

from pytest import raises

from art_deco.core.specs.static_arg_specs import ArgKind, Sentinels, StaticArgSpec, StaticArgSpecs
from art_deco.core.specs.static_inspector import get_static_arg_specs
from art_deco_test_examples.classes.std_and_attrs_dataclasses import (
    EXPECTED_ATTRS_DATA_CLASS,
    EXPECTED_STD_DATA_CLASS,
    AttrsDataClass,
    StdDataClass,
)
from art_deco_test_examples.functions.annotated_funcs import (
    PARSED_ANNOTATED_FUNCS,
    func_annotated_new_style,
    func_annotated_old_style,
)
from art_deco_test_examples.functions.async_funcs import ASYNC_FUNC, async_func
from art_deco_test_examples.functions.simple_funcs import PARSED_SIMPLE_FUNCS, func_with_default, simple_func
from art_deco_test_examples.functions.var_arg_and_kwonly_funcs import (
    PARSED_VAR_ARG_FUNCS,
    func_with_kwonly,
    func_with_var_args_and_kwargs,
)
from art_deco_test_examples.methods.normal_methods import ExampleClass


def test_get_static_arg_specs_with_funcs() -> None:
    assert get_static_arg_specs(simple_func, parse_type_hints=True) == PARSED_SIMPLE_FUNCS[simple_func]

    assert get_static_arg_specs(func_with_default, parse_type_hints=True) == PARSED_SIMPLE_FUNCS[func_with_default]

    assert (
        get_static_arg_specs(func_annotated_old_style, parse_type_hints=True)
        == PARSED_ANNOTATED_FUNCS[func_annotated_old_style][True]
    )
    assert (
        get_static_arg_specs(func_annotated_old_style, parse_type_hints=False)
        == PARSED_ANNOTATED_FUNCS[func_annotated_old_style][False]
    )

    if sys.version_info[:2] < (3, 10):
        with raises(TypeError):
            get_static_arg_specs(func_annotated_new_style, parse_type_hints=True)
    else:
        assert (
            get_static_arg_specs(func_annotated_new_style, parse_type_hints=True).args
            == get_static_arg_specs(func_annotated_old_style, parse_type_hints=True).args
        )
    assert (
        get_static_arg_specs(func_annotated_new_style, parse_type_hints=False)
        == PARSED_ANNOTATED_FUNCS[func_annotated_new_style][False]
    )

    assert get_static_arg_specs(func_with_kwonly, parse_type_hints=True) == PARSED_VAR_ARG_FUNCS[func_with_kwonly][True]
    assert (
        get_static_arg_specs(func_with_var_args_and_kwargs, parse_type_hints=True)
        == PARSED_VAR_ARG_FUNCS[func_with_var_args_and_kwargs][True]
    )
    assert (
        get_static_arg_specs(func_with_var_args_and_kwargs, parse_type_hints=False)
        == PARSED_VAR_ARG_FUNCS[func_with_var_args_and_kwargs][False]
    )

    assert get_static_arg_specs(async_func, parse_type_hints=True) == ASYNC_FUNC


def test_get_static_arg_specs_methods() -> None:
    def expected_static(method: Callable) -> StaticArgSpecs:
        return StaticArgSpecs(
            args=[
                StaticArgSpec(
                    name='x', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
                ),
                StaticArgSpec(
                    name='y',
                    kind=ArgKind.POSITIONAL_OR_KEYWORD,
                    annotation=List[float],
                    default_val=Sentinels.NO_DEFAULT_VALUE,
                ),
                StaticArgSpec(name='z', kind=ArgKind.POSITIONAL_OR_KEYWORD, annotation=Optional[str], default_val=None),
                StaticArgSpec(
                    name='args', kind=ArgKind.VAR_POSITIONAL, annotation=int, default_val=Sentinels.NO_DEFAULT_VALUE
                ),
                StaticArgSpec(
                    name='some_keyword',
                    kind=ArgKind.KEYWORD_ONLY,
                    annotation=float,
                    default_val=Sentinels.NO_DEFAULT_VALUE,
                ),
                StaticArgSpec(
                    name='kwargs', kind=ArgKind.VAR_KEYWORD, annotation=float, default_val=Sentinels.NO_DEFAULT_VALUE
                ),
            ],
            sig=inspect.signature(method),
        )

    # pylint: disable=no-member
    res1 = get_static_arg_specs(ExampleClass().func_with_var_args_and_kwargs_normal, parse_type_hints=True)
    assert res1 == expected_static(ExampleClass().func_with_var_args_and_kwargs_normal)

    res2 = get_static_arg_specs(ExampleClass.func_with_var_args_and_kwargs_class, parse_type_hints=True)
    assert res2 == expected_static(ExampleClass.func_with_var_args_and_kwargs_class)

    res3 = get_static_arg_specs(ExampleClass.func_with_var_args_and_kwargs_static, parse_type_hints=True)
    assert res3 == expected_static(ExampleClass.func_with_var_args_and_kwargs_static)


def test_get_static_arg_specs_classes() -> None:
    res1 = get_static_arg_specs(StdDataClass, parse_type_hints=True)
    assert res1.args[:-1] == EXPECTED_STD_DATA_CLASS.args
    res2 = get_static_arg_specs(AttrsDataClass, parse_type_hints=True)
    assert res2 == EXPECTED_ATTRS_DATA_CLASS
