from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import nox

LIB_ROOT = Path(__file__).parent
CORE_REQS = LIB_ROOT / '3rdparty/requirements.txt'
DEV_REQS = LIB_ROOT / '3rdparty/requirements-dev.txt'


@dataclass
class ExtraDeps:
    include: list[str]
    exclude: list[str]


TYPING_EXTENSIONS_DEPS = (
    ExtraDeps(['typing_extensions'], []),
    ExtraDeps(['typing_extensions~=4.4'], []),
    ExtraDeps(['typing_extensions~=4.3'], []),
    ExtraDeps(['typing_extensions~=4.2'], []),
    ExtraDeps(['typing_extensions~=4.1'], []),
    ExtraDeps(['typing_extensions~=4.0'], ['pydantic']),
    ExtraDeps(['typing_extensions~=3.10'], ['pydantic']),
    ExtraDeps(['typing_extensions~=3.7'], ['pydantic']),
    ExtraDeps(['typing_extensions~=3.6 ; python_version <= "3.8"'], ['pydantic']),
)


def get_reqs(*paths: Path, extra_deps: list[ExtraDeps]) -> list[str]:
    all_reqs: list[str] = []
    for path in paths:
        reqs = path.resolve().read_text(encoding='utf-8').replace('\r', '').split('\n')
        all_reqs.extend(reqs)
    reqs_set = set(all_reqs)
    reqs_set = reqs_set - {exclude for dep in extra_deps for exclude in dep.exclude}
    return [req for req in all_reqs if req and req in reqs_set]


@nox.session(reuse_venv=True)
@nox.parametrize('t_ext', TYPING_EXTENSIONS_DEPS)
def tests(session: nox.Session, t_ext: ExtraDeps) -> None:
    session.install(*get_reqs(CORE_REQS, DEV_REQS, extra_deps=[t_ext]))
    session.run('make', 'test', external=True)
