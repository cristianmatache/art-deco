from art_deco.core.specs.dynamic_inspector import get_dynamic_arg_specs
from art_deco.core.specs.static_inspector import get_static_arg_specs
from art_deco.utils.dynamic_args import dynamic_specs_to_dict
from art_deco_test_examples.functions.simple_funcs import simple_func
from art_deco_test_examples.functions.var_arg_and_kwonly_funcs import func_with_var_args_and_kwargs
from art_deco_test_examples.methods.normal_methods import ExampleClass


def test_get_dynamic_arg_specs_with_funcs() -> None:
    static_simple_func = get_static_arg_specs(simple_func, parse_type_hints=True)
    res1 = get_dynamic_arg_specs(static_simple_func, args=(1,), kwargs={})
    assert dynamic_specs_to_dict(res1) == [{'name': 'x', 'value': 1, 'called_as_kw': False}]
    res2 = get_dynamic_arg_specs(static_simple_func, args=(), kwargs={'x': 1})
    assert dynamic_specs_to_dict(res2) == [{'name': 'x', 'value': 1, 'called_as_kw': True}]

    static_var_args = get_static_arg_specs(func_with_var_args_and_kwargs, parse_type_hints=False)
    res3 = get_dynamic_arg_specs(
        static_var_args, args=(1, [2], '3', '4', 5, 6, 7), kwargs=dict(some_keyword=10, a=1, b=2)
    )
    assert dynamic_specs_to_dict(res3) == [
        {'name': 'x', 'value': 1, 'called_as_kw': False},
        {'name': 'y', 'value': [2], 'called_as_kw': False},
        {'name': 'z', 'value': '3', 'called_as_kw': False},
        {'name': 't', 'value': '4', 'called_as_kw': False},
        {'name': '__art_deco_auto_name__0', 'value': 5, 'called_as_kw': False},
        {'name': '__art_deco_auto_name__1', 'value': 6, 'called_as_kw': False},
        {'name': '__art_deco_auto_name__2', 'value': 7, 'called_as_kw': False},
        {'name': 'some_keyword', 'value': 10, 'called_as_kw': True},
        {'name': 'a', 'value': 1, 'called_as_kw': True},
        {'name': 'b', 'value': 2, 'called_as_kw': True},
    ]
    assert res3.args_by_name['__art_deco_auto_name__1'].static is res3.args_by_name['__art_deco_auto_name__0'].static
    assert res3.args_by_name['__art_deco_auto_name__2'].static is res3.args_by_name['__art_deco_auto_name__0'].static
    assert res3.args_by_name['a'].static is res3.args_by_name['b'].static
    res4 = get_dynamic_arg_specs(static_var_args, args=(), kwargs=dict(x=1, y=[2], z='3', some_keyword=10))
    assert dynamic_specs_to_dict(res4) == [
        {'name': 'x', 'value': 1, 'called_as_kw': True},
        {'name': 'y', 'value': [2], 'called_as_kw': True},
        {'name': 'z', 'value': '3', 'called_as_kw': True},
        {'name': 'some_keyword', 'value': 10, 'called_as_kw': True},
        {'name': 't', 'value': None, 'called_as_kw': True},
    ]


def test_get_dynamic_arg_specs_methods() -> None:
    # pylint: disable=no-member
    static_args = get_static_arg_specs(ExampleClass().func_with_var_args_and_kwargs_normal, parse_type_hints=True)
    res1 = get_dynamic_arg_specs(static_args, args=(1, [2], '', 3), kwargs={'some_keyword': 1, 'other_kw': 2})
    assert dynamic_specs_to_dict(res1) == [
        {'name': 'x', 'value': 1, 'called_as_kw': False},
        {'name': 'y', 'value': [2], 'called_as_kw': False},
        {'name': 'z', 'value': '', 'called_as_kw': False},
        {'name': '__art_deco_auto_name__0', 'value': 3, 'called_as_kw': False},
        {'name': 'some_keyword', 'value': 1, 'called_as_kw': True},
        {'name': 'other_kw', 'value': 2, 'called_as_kw': True},
    ]
    assert res1.args_by_name['x'].static == static_args.args_by_name['x']
    assert res1.args_by_name['some_keyword'].static == static_args.args_by_name['some_keyword']
    assert res1.args_by_name['__art_deco_auto_name__0'].static == static_args.args_by_name['args']
    assert res1.args_by_name['other_kw'].static == static_args.args_by_name['kwargs']

    static_args_cls = get_static_arg_specs(ExampleClass.func_with_var_args_and_kwargs_class, parse_type_hints=True)
    res2 = get_dynamic_arg_specs(static_args_cls, args=(1, [2], '', 3), kwargs={'some_keyword': 1, 'other_kw': 2})
    assert dynamic_specs_to_dict(res2) == dynamic_specs_to_dict(res1)

    static_args_static = get_static_arg_specs(ExampleClass.func_with_var_args_and_kwargs_static, parse_type_hints=True)
    res3 = get_dynamic_arg_specs(static_args_static, args=(1, [2], '', 3), kwargs={'some_keyword': 1, 'other_kw': 2})
    assert dynamic_specs_to_dict(res3) == dynamic_specs_to_dict(res1)
