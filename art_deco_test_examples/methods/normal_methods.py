# pylint: disable=keyword-arg-before-vararg,unused-argument  # pylint false positive
from __future__ import annotations

from typing import List, Optional, Type


class ExampleClass:

    # noinspection PyMethodMayBeStatic
    def func_with_var_args_and_kwargs_normal(
        self, x: int, y: List[float], z: Optional[str] = None, *args: int, some_keyword: float, **kwargs: float
    ) -> float:
        return x

    @classmethod
    def func_with_var_args_and_kwargs_class(
        cls: Type,
        x: int,
        y: List[float],
        z: Optional[str] = None,
        *args: int,
        some_keyword: float,
        **kwargs: float,
    ) -> float:
        return x

    @staticmethod
    def func_with_var_args_and_kwargs_static(
        x: int, y: List[float], z: Optional[str] = None, *args: int, some_keyword: float, **kwargs: float
    ) -> float:
        return x
