"""Architecture checks import-linter cannot express (ARC-016..018, STR-012, SCR-010).

Each test asserts it inspected something, so a typo cannot make it pass vacuously (ARC-018).
"""

import ast
from pathlib import Path

SRC = Path(__file__).resolve().parents[3] / "src" / "reference_service"
CANONICAL_PACKAGES = [
    "api",
    "api/routers",
    "api/schemas",
    "domain",
    "domain/models",
    "domain/rules",
    "domain/services",
    "application",
    "application/use_cases",
    "adapters",
    "adapters/db",
    "adapters/http_clients",
    "adapters/queue",
    "adapters/storage",
    "adapters/keyvault",
    "ai",
    "ai/agents",
    "ai/tools",
    "security",
    "common",
]
ENV_READERS = {"os.environ", "os.getenv", "os.environb", "os.putenv"}


def _dotted(node: ast.AST) -> str:
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return node.id if isinstance(node, ast.Name) else ""


def test_every_canonical_package_exists_with_init() -> None:
    missing = [p for p in CANONICAL_PACKAGES if not (SRC / p / "__init__.py").is_file()]
    assert missing == []


def test_only_config_reads_the_environment() -> None:
    files = sorted(SRC.rglob("*.py"))
    assert len(files) > len(CANONICAL_PACKAGES)  # non-vacuous
    offenders = []
    for path in files:
        if path.name == "config.py" and path.parent == SRC:
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if _dotted(node) in ENV_READERS:
                offenders.append(f"{path.relative_to(SRC)}: {_dotted(node)}")
            if isinstance(node, ast.ImportFrom) and node.module == "os":
                offenders += [
                    f"{path.relative_to(SRC)}: from os import {a.name}"
                    for a in node.names
                    if a.name in {"environ", "getenv", "environb"}
                ]
    assert offenders == []
    assert (SRC / "config.py").is_file()


def test_no_print_calls_in_src() -> None:
    """OBS-001: print() must not appear in src/."""
    offenders = [
        str(path.relative_to(SRC))
        for path in SRC.rglob("*.py")
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
        if isinstance(node, ast.Call) and _dotted(node.func) == "print"
    ]
    assert offenders == []
