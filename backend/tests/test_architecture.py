"""Architecture invariants enforced as tests (AST scan, no imports executed)."""

import ast
from pathlib import Path

RIPPLE = Path(__file__).resolve().parents[1] / "ripple"
REASONING_LAYERS = ("agent", "planning", "evidence")


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    return names


def test_reasoning_layers_never_import_the_simulator() -> None:
    """agent/, planning/, evidence/ must not import ripple.simulator (hidden truth, invariant #2)."""
    offenders = [
        f"{path.relative_to(RIPPLE)} imports {name}"
        for layer in REASONING_LAYERS
        for path in (RIPPLE / layer).rglob("*.py")
        for name in _imports(path)
        if name.startswith("ripple.simulator")
    ]
    assert offenders == []


def test_ground_truth_only_used_inside_simulator() -> None:
    offenders = [
        str(path.relative_to(RIPPLE))
        for path in RIPPLE.rglob("*.py")
        if "simulator" not in path.relative_to(RIPPLE).parts
        and any(name.startswith("ripple.simulator.ground_truth") for name in _imports(path))
    ]
    assert offenders == []


def test_cypher_only_executed_in_graph_package() -> None:
    """Only ripple/graph/ calls .query()/.ro_query(), keeping all Cypher auditable (D-003)."""
    offenders = []
    for path in RIPPLE.rglob("*.py"):
        if path.relative_to(RIPPLE).parts[0] == "graph":
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"query", "ro_query"}
            ):
                offenders.append(f"{path.relative_to(RIPPLE)}:{node.lineno}")
    assert offenders == []
