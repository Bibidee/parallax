import importlib.util
import json
import sys
import types
from pathlib import Path


def load_module():
    class Decorator:
        def __call__(self, fn):
            return fn
        @property
        def payable(self):
            return self

    fake_gl = types.SimpleNamespace()
    fake_gl.Contract = type("Contract", (), {})
    fake_gl.Event = type("Event", (), {})
    fake_gl.public = types.SimpleNamespace(write=Decorator(), view=Decorator())
    fake_gl.evm = types.SimpleNamespace(contract_interface=lambda cls: cls)
    fake_gl.vm = types.SimpleNamespace(UserError=ValueError, Return=object)
    fake = types.ModuleType("genlayer")
    fake.gl = fake_gl
    fake.Address = type("Address", (), {"__init__": lambda self, value="": setattr(self, "as_hex", str(value))})
    fake.u256 = int
    fake.TreeMap = dict
    fake.allow_storage = lambda cls: cls
    old = sys.modules.get("genlayer")
    sys.modules["genlayer"] = fake
    try:
        spec = importlib.util.spec_from_file_location("parallax_helpers", Path("contracts/parallax.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        if old is None:
            sys.modules.pop("genlayer", None)
        else:
            sys.modules["genlayer"] = old


def analysis(**changes):
    value = {"spec_match": "yes", "visual_change": "yes", "evidence_support": "yes",
             "evidence_quality": "strong", "risk": "no", "confidence": 90,
             "rationale": "Supported by all committed artifacts."}
    value.update(changes)
    return value


def test_approval_requires_complete_safe_tuple():
    m = load_module()
    assert m.derive_verdict(analysis()) == "approved"
    for key, value in (("spec_match", "no"), ("visual_change", "unclear"), ("evidence_support", "no"), ("risk", "yes"), ("evidence_quality", "weak"), ("confidence", 74)):
        assert m.derive_verdict(analysis(**{key: value})) == "blocked"


def test_equivalence_ignores_rationale_and_confidence_but_not_decision_facts():
    m = load_module()
    assert m.equivalent_analysis(analysis(confidence=75, rationale="one"), analysis(confidence=100, rationale="two"))
    assert m.equivalent_analysis(analysis(risk="yes"), analysis(spec_match="no", visual_change="unclear", rationale="different reason"))
    assert not m.equivalent_analysis(analysis(), analysis(risk="yes"))
    assert not m.equivalent_analysis(analysis(), {"bad": True})


def test_normalized_hash_and_url_guards():
    m = load_module()
    digest = "0x" + "ab" * 32
    assert m.canonical_hash(digest.upper()) == digest
    for bad in ("0x00", "ab" * 32, "0x" + "zz" * 32):
        try:
            m.canonical_hash(bad)
        except Exception:
            pass
        else:
            assert False
    assert m.valid_url("https://public.example/item", "url")
    for bad in ("http://public.example", "https://localhost/x", "https://127.0.0.1/x", "https://10.0.0.1/x", "https://172.016.0.1/x", "https://0x7f.0.0.1/x", "https://0x7f.1/x", "https://127.1/x", "https://2130706433/x", "https://0x7f000001/x", "https://[::1]/x", "https://[fc00::1]/x", "https://[fe80::1]/x", "https://user@public.example/x", "https://public.example\\@127.0.0.1/x"):
        try:
            m.valid_url(bad, "url")
        except Exception:
            pass
        else:
            assert False, bad


def test_text_and_identifier_bounds():
    m = load_module()
    assert m.text("  hello   world ", "text") == "hello world"
    assert m.identifier("PX-1") == "PX-1"
    for bad in ("", " ", "not allowed!", "x" * 97):
        try:
            m.identifier(bad)
        except Exception:
            pass
        else:
            assert False, bad


def test_manifest_like_serialization_is_deterministic():
    m = load_module()
    payload = json.dumps({"b": 2, "a": 1}, sort_keys=True, separators=(",", ":"))
    assert payload == '{"a":1,"b":2}'
    assert m.clean("\x00  a\n b  ") == "a b"


def test_artifact_fault_classes_are_nonsemantic():
    m = load_module()
    assert m.technical_failure(m.FAIL_SPONSOR_ARTIFACT, "hash_mismatch")["kind"] == "technical"
    assert m.technical_failure(m.FAIL_WORKER_ARTIFACT, "invalid_utf8")["fault_class"] == "worker_artifact"
    assert m.equivalent_analysis(analysis(risk="yes"), analysis(spec_match="no", rationale="different semantic reason"))
