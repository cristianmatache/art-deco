from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from typing_extensions import get_type_hints


@dataclass
class TypeHintsParser:
    func: Callable

    def parse(self) -> dict[str, Any]:
        return get_type_hints(self.func)


@dataclass
class ExtrasTypeHintsParser(TypeHintsParser):
    def parse(self) -> dict[str, Any]:
        return get_type_hints(self.func, include_extras=True)
