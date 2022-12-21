from __future__ import annotations

from typing import Hashable, TypeVar

_K = TypeVar('_K', bound=Hashable)
_V = TypeVar('_V')


def select_keys(dictionary: dict[_K, _V], keys: list[_K]) -> dict[_K, _V]:
    return {key: value for key, value in dictionary.items() if key in keys}
