# Art Deco

[//]: # "add-your-build-status-badge-here"

[![Python package CI](https://github.com/cristianmatache/art-deco/actions/workflows/ci.yml/badge.svg)](https://github.com/cristianmatache/art-deco/actions/workflows/ci.yml)
[![powered_by_alpha_build](https://img.shields.io/badge/Powered%20by%20-AlphaBuild-lightblue?style=flat&logo=CMake&logoColor=lightblue)
](https://github.com/cristianmatache/alpha-build)
[![Python 3.8+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
![pylint Score](https://mperlet.github.io/pybadge/badges/10.svg)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Description

Art Deco is a library that, via decorators, makes complex processing of function/method arguments effortless.
Use cases for `art_deco` include, but are not limited to:

- data validation (e.g., validating the inputs of a function)
- input conversion (e.g., type coercion based on type annotations)
- deserializing / parsing (e.g., parse JSONs or decode MessagePack into Python objects based on type annotations)
- caching

That is, this library shines when one needs to build a decorator that processes inputs based on:
the _inspected signature_ of the function arguments (e.g., needs access to argument names, type annotations,
default values), or _runtime information_ like discerning whether an argument was called positionally or as a keyword,
as part of a variable argument (i.e., `*args`, `**kwargs`) etc.

Therefore, it works like a charm in conjunction with any data validation library (e.g.,
`cerberus`, `pandera`) or any library that consumes data from the external world - network, Excel etc.
(e.g., `flask`, `plotly dash`, `pyxll`, `xlwings`).

Moreover, `art_deco` handles several Python language constructs:

- functions, regular methods, static methods, class methods
- sync and `async`
- metaclasses and classes (regular classes, `dataclasses`, `attrs` classes, `pydantic` models and data classes)
- variable arguments (i.e., `*args`, `**kwargs`)
- positional only, keyword only arguments

and provides:

- `art_deco.core`: a fundamental layer based on which one can implement any argument processing logic.
- `art_deco.hack_args`: a convenient, pre-packaged argument processor implemented on top of `art_deco.core`.

## Getting Started

### Installation

```bash
pip install art_deco
```

### Hacking function arguments

To illustrate what can be achieved, let's start with a few toy usages of `art_deco.hack_args`.

```python
from __future__ import annotations

from art_deco.hack_args import marks
from art_deco.hack_args.processor import hack_args

@marks.arg_hacker
def hack_x(x: int | float | str) -> str:
    """Function used for data validation and type coercion."""
    assert float(x) < 100, f'Validation failed: {x} must be < 100'
    return str(x) if isinstance(x, (int, float)) else x

@hack_args({'x': hack_x})
def func(x):
    """Function with a processed argument."""
    return x

assert func('1') == func(1) == '1'
# func(200) ----> Errors with AssertionError, thanks to data validation
```

the same thing can be achieved via the `Annotated` type hint:

```python
from typing_extensions import Annotated

@hack_args()
def func(x: Annotated[str, hack_x]) -> str:
    """Function with a processed argument."""
    return x
```

To validate more than one argument at a time:

```python
from art_deco.core.arg_processors.api import Context


@marks.wide_validator
def validate_x_y(_: Context, x: str, y: str) -> None:
  """Validate 2 arguments."""
  # Context is an internal concept that allows users to use static information like the inspected signature or
  # default values, as well as call runtime information like what arguments were called positionally.
  if x.startswith('1'):
    assert y.startswith('2'), f'Validation failed: {x} starts with 1, but {y} does not start with 2'


@hack_args({'x': hack_x, 'y': hack_x, ('x', 'y'): validate_x_y})
def func(x, y):
  """Function with 2 processed arguments."""
  return f'x={x}, y={y}'


# Similarly we could use `Annotated`
@hack_args()
def func(x: Annotated[str, hack_x, validate_x_y], y: Annotated[str, hack_x, validate_x_y]) -> str:
  """Function with 2 processed arguments."""
  return f'x={x}, y={y}'
```

### Implementing a new argument processor

In `art_deco.core`, there are 2 types of argument processors:

- **static:** initialized once, at function definition time, arguments to be processed are determined once as well,
  while the actual argument processing happens every time the decorated function is called.
- **dynamic:** initialized every time the decorated function is called, arguments to be processed and the actual
  argument processing happen every time the decorated functions is called.

Let's look at a static example, since a dynamic processor would have a nearly identical interface.

```python
from __future__ import annotations

from typing import Any, Mapping

from art_deco.core.arg_processors.api import ArgNames, Context, MultiArgValidateFunc
from art_deco.core.arg_processors.static_decorator import static_process_args
from art_deco.core.specs.static_arg_specs import StaticArgSpecs
from art_deco.core.specs.dynamic_arg_specs import DynamicArgSpec

class SimpleCastingProcessor:
    def __init__(self, static_args: StaticArgSpecs) -> None:
        self.static_args = static_args
        self.hacks: dict[str, Any] = {}
        for arg in static_args.args:
            if arg.has_annotation:
                self.hacks[arg.name] = arg.annotation

    def should_process_arg(self, arg: str) -> bool:
        """Hook function called to determine whether to process an argument or not, always by name."""
        return arg in self.hacks

    def process_arg(self, arg: DynamicArgSpec, _: Context) -> Any:
        """This function specifies how to actually process the argument."""
        if arg.is_default:  # If the value is the default one, do not run any casting
            return arg.value
        return self.hacks[arg.name](arg.value)  # Get the annotation for the argument name and coerce the supplied value

    def get_wide_checks(self) -> Mapping[ArgNames, MultiArgValidateFunc]:  # No logic for "wide" checks.
        return {}


@static_process_args(SimpleCastingProcessor)
def coercion(x: int, y: float) -> float:
    return x + y

assert coercion('1', '2') == 3
assert coercion('1', 2) == 3
assert coercion(1, 2) == 3
```

## Development

Read [CONTRIBUTING.md](CONTRIBUTING.md).
