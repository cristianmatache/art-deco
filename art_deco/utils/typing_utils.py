from __future__ import annotations

from typing import Any, Generic, TypeVar

from typing_extensions import Annotated

T = TypeVar('T')
S = TypeVar('S')


def is_annotated(hint: Any) -> bool:  # Use TypeGuard
    # pylint: disable=import-outside-toplevel
    extensions_annotated_type = type(Annotated[Any, 'art_deco'])
    try:
        from typing import Annotated as TypingAnnotated  # type: ignore[attr-defined] # noqa: WPS433
    except ImportError:

        class TypingAnnotated(Generic[T, S]):  # type:ignore[no-redef] # noqa: WPS431, WPS440
            """Placeholder."""

    std_annotated_type = type(TypingAnnotated[Any, 'art_deco'])
    return isinstance(hint, (extensions_annotated_type, std_annotated_type))
