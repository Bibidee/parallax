"""Regression checks for GenVM event topic/blob serialization limits."""

import ast
from pathlib import Path


SOURCE = Path(__file__).parents[1] / "contracts" / "parallax.py"
EXPECTED_INDEXED = {
    "JobCreated": ["job_id", "sponsor", "worker"],
    "EvidenceSubmitted": ["job_id", "worker"],
    "JobReviewed": ["job_id", "verdict"],
    "JobSettled": ["job_id", "outcome"],
    "JobCancelled": ["job_id", "sponsor"],
    "JobExpired": ["job_id"],
}
EXPECTED_BLOB_KWARGS = {
    "JobCreated": {"reward"},
    "EvidenceSubmitted": {"bond"},
    "JobReviewed": {"confidence"},
    "JobSettled": {"sponsor_amount", "worker_amount"},
    "JobCancelled": set(),
    "JobExpired": set(),
}


def _event_classes(tree):
    result = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue
        if not any(isinstance(base, ast.Attribute) and base.attr == "Event" for base in node.bases):
            continue
        init = next((item for item in node.body if isinstance(item, ast.FunctionDef) and item.name == "__init__"), None)
        assert init is not None, f"{node.name} must declare an initializer"
        indexed = [arg.arg for arg in init.args.posonlyargs if arg.arg != "self"]
        result[node.name] = indexed
    return result


def _event_emits(tree):
    result = {name: [] for name in EXPECTED_INDEXED}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute) or node.func.attr != "emit":
            continue
        constructor = node.func.value
        if not isinstance(constructor, ast.Call) or not isinstance(constructor.func, ast.Name):
            continue
        name = constructor.func.id
        if name in result:
            result[name].append((len(constructor.args), {kw.arg for kw in constructor.keywords if kw.arg is not None}))
    return result


def test_every_event_uses_at_most_three_indexed_fields_and_explicit_blobs():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    assert _event_classes(tree) == EXPECTED_INDEXED
    emits = _event_emits(tree)
    for name, expected_kwargs in EXPECTED_BLOB_KWARGS.items():
        assert emits[name], f"{name} must be emitted"
        for positional_count, keyword_names in emits[name]:
            assert positional_count <= 3, f"{name} exceeds GenVM's three indexed topic limit"
            assert expected_kwargs.issubset(keyword_names), f"{name} payout metadata must be emitted in the blob"
