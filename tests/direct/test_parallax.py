import hashlib
import json
from conftest import warp_to
from gltest.direct import sdk_loader


# genlayer-test 0.29.2 otherwise asks for the retired default rc7 artifact.
# Pin the known-compatible runner used by the current Direct Mode suite.
sdk_loader.get_latest_version = lambda: "v0.2.12"


CONTRACT = "contracts/parallax.py"
NOW = 1_787_040_000
ONE = 10**18
BASELINE_URL = "https://baseline.example/parallax-001"
TARGET_URL = "https://target.example/parallax-001"
BEFORE_URL = "https://before.example/parallax-001.png"
AFTER_URL = "https://after.example/parallax-001.png"
REPORT_URL = "https://report.example/parallax-001"
BASELINE = b"State before: the component is not installed."
TARGET = b"State after: the component is installed and operational."
REPORT = b"Completion report: component installed and operational."
BEFORE_IMAGE = b"before-image-bytes"
AFTER_IMAGE = b"after-image-bytes"


def digest(raw):
    return "0x" + hashlib.sha256(raw).hexdigest()


def create_args(worker, deadline=NOW + 86400, bond=ONE // 10):
    return ("PX-001", worker, "PARALLAX-001: install the component and leave it operational.",
            BASELINE_URL, digest(BASELINE), TARGET_URL, digest(TARGET),
            BEFORE_URL, digest(BEFORE_IMAGE), AFTER_URL, digest(AFTER_IMAGE), bond, deadline)


def deploy(direct_deploy, direct_vm):
    contract = direct_deploy(CONTRACT)
    import sys
    direct_vm._parallax_module = sys.modules[contract.__class__.__module__]
    warp_to(direct_vm, "2026-08-18T08:00:00Z")
    return contract


def create(contract, direct_vm, direct_alice, direct_bob, value=2 * ONE):
    direct_vm.sender, direct_vm.value = direct_alice, value
    try:
        contract.create_job(*create_args(direct_bob))
    finally:
        direct_vm.value = 0


def submit(contract, direct_vm, direct_bob, value=ONE // 10):
    direct_vm.sender, direct_vm.value = direct_bob, value
    try:
        contract.submit_evidence("PX-001", REPORT_URL, digest(REPORT), "The component is installed and operational.")
    finally:
        direct_vm.value = 0


def configure(vm, result, marker="PARALLAX-001"):
    vm.mock_web(BASELINE_URL, {"status": 200, "body": BASELINE})
    vm.mock_web(TARGET_URL, {"status": 200, "body": TARGET})
    vm.mock_web(REPORT_URL, {"status": 200, "body": REPORT})
    vm.mock_web(BEFORE_URL, {"status": 200, "body": BEFORE_IMAGE})
    vm.mock_web(AFTER_URL, {"status": 200, "body": AFTER_IMAGE})
    vm.mock_llm(marker, json.dumps(result))


SAFE = {"spec_match": "yes", "visual_change": "yes", "evidence_support": "yes",
        "evidence_quality": "strong", "risk": "no", "confidence": 90,
        "rationale": "The committed text and images support the requested change."}


def test_create_and_read_persists_exact_commitments(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm)
    create(contract, direct_vm, direct_alice, direct_bob)
    job = contract.get_job("PX-001")
    assert job["status"] == "pending"
    assert job["sponsor"].lower() == "0x" + direct_alice.hex()
    assert job["worker"].lower() == "0x" + direct_bob.hex()
    assert job["reward_deposited"] == str(2 * ONE)
    assert job["worker_bond_held"] == "0"
    assert contract.get_info()["version"] == "0.2.0"


def test_create_guards_and_deadline(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm)
    direct_vm.sender, direct_vm.value = direct_alice, ONE
    with direct_vm.expect_revert(): contract.create_job(*create_args(direct_bob, deadline=NOW))
    with direct_vm.expect_revert(): contract.create_job(*create_args(bytes(20)))
    bad = list(create_args(direct_bob)); bad[2] = " "
    with direct_vm.expect_revert(): contract.create_job(*bad)
    same = list(create_args(direct_bob)); same[10] = same[8]
    with direct_vm.expect_revert(): contract.create_job(*same)


def test_submission_requires_worker_and_exact_bond(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender, direct_vm.value = direct_alice, ONE // 10
    with direct_vm.expect_revert(): contract.submit_evidence("PX-001", REPORT_URL, digest(REPORT), "report")
    direct_vm.sender, direct_vm.value = direct_bob, 1
    with direct_vm.expect_revert(): contract.submit_evidence("PX-001", REPORT_URL, digest(REPORT), "report")
    direct_vm.value = ONE // 10
    contract.submit_evidence("PX-001", REPORT_URL, digest(REPORT), "report")
    assert contract.get_job("PX-001")["status"] == "submitted"


def test_review_uses_verified_artifacts_and_approves(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    configure(direct_vm, SAFE)
    direct_vm.sender = direct_alice
    contract.review("PX-001")
    job = contract.get_job("PX-001")
    assert job["status"] == "approved" and job["verdict"] == "approved" and job["confidence"] == "90"


def test_semantic_rejection_is_blocked_and_settlement_is_one_time(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    configure(direct_vm, dict(SAFE, risk="yes", confidence=90))
    direct_vm.sender = direct_bob; contract.review("PX-001")
    assert contract.get_job("PX-001")["status"] == "blocked"
    contract.settle("PX-001")
    assert contract.get_job("PX-001")["status"] == "settled"
    with direct_vm.expect_revert(): contract.settle("PX-001")


def test_cancel_pending_refunds_and_cannot_repeat(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice; contract.cancel_job("PX-001")
    assert contract.get_job("PX-001")["status"] == "cancelled"
    with direct_vm.expect_revert(): contract.cancel_job("PX-001")


def test_withdrawal_returns_worker_bond(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    # A worker cannot withdraw while the submitted evidence is reviewable.
    with direct_vm.expect_revert(): contract.withdraw_evidence("PX-001")
    direct_vm.mock_web(BASELINE_URL, {"status": 503, "body": b""})
    direct_vm.sender = direct_alice; contract.review("PX-001")
    warp_to(direct_vm, "2026-08-19T08:00:00Z")
    direct_vm.sender = direct_bob; contract.withdraw_evidence("PX-001")
    job = contract.get_job("PX-001")
    assert job["status"] == "cancelled" and job["worker_bond_held"] == "0"


def test_artifact_mismatch_fails_closed(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    configure(direct_vm, SAFE)
    direct_vm._web_mocks.clear()
    direct_vm.mock_web(BASELINE_URL, {"status": 200, "body": b"changed"})
    direct_vm.mock_web(TARGET_URL, {"status": 200, "body": TARGET})
    direct_vm.mock_web(REPORT_URL, {"status": 200, "body": REPORT})
    direct_vm.mock_web(BEFORE_URL, {"status": 200, "body": BEFORE_IMAGE})
    direct_vm.mock_web(AFTER_URL, {"status": 200, "body": AFTER_IMAGE})
    direct_vm.sender = direct_alice; contract.review("PX-001")
    job = contract.get_job("PX-001")
    assert job["status"] == "retryable"
    assert job["failure_class"] in ("sponsor_artifact", "infrastructure")


def test_permissionless_expiry_refunds_both_and_is_one_time(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    warp_to(direct_vm, "2026-08-19T08:00:00Z")
    direct_vm.sender = direct_bob
    contract.expire_job("PX-001")
    job = contract.get_job("PX-001")
    assert job["status"] == "settled" and job["reward_deposited"] == "0" and job["worker_bond_held"] == "0"
    with direct_vm.expect_revert(): contract.expire_job("PX-001")


def test_finalized_jobs_release_active_capacity(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm)
    import sys
    module = sys.modules[contract.__class__.__module__]
    original_limit = module.MAX_ACTIVE_JOBS
    module.MAX_ACTIVE_JOBS = 1
    try:
        create(contract, direct_vm, direct_alice, direct_bob)
        direct_vm.sender = direct_alice
        contract.cancel_job("PX-001")
        args = list(create_args(direct_bob)); args[0] = "PX-002"
        direct_vm.value = 2 * ONE
        contract.create_job(*args)
    finally:
        module.MAX_ACTIVE_JOBS = original_limit


def test_sponsor_artifact_failure_never_slashes_worker_bond(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    direct_vm.mock_web(BASELINE_URL, {"status": 503, "body": b""})
    direct_vm.sender = direct_alice; contract.review("PX-001")
    warp_to(direct_vm, "2026-08-19T08:00:00Z")
    contract.settle("PX-001")
    assert contract.get_job("PX-001")["status"] == "settled"
    info = contract.get_info()
    assert info["total_paid_to_workers"] == str(ONE // 10)


def test_worker_artifact_failure_is_retryable_and_refunded(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob)
    bad_report = b"\xff\xfe"
    direct_vm.sender, direct_vm.value = direct_bob, ONE // 10
    contract.submit_evidence("PX-001", REPORT_URL, digest(bad_report), "report")
    direct_vm.value = 0
    direct_vm.mock_web(REPORT_URL, {"status": 200, "body": bad_report})
    direct_vm.sender = direct_alice; contract.review("PX-001")
    job = contract.get_job("PX-001")
    assert job["status"] == "retryable" and job["failure_class"] in ("worker_artifact", "infrastructure")
    warp_to(direct_vm, "2026-08-19T08:00:00Z")
    contract.expire_job("PX-001")
    assert contract.get_job("PX-001")["status"] == "settled"


def test_validator_disagreement_on_approval_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = deploy(direct_deploy, direct_vm); create(contract, direct_vm, direct_alice, direct_bob); submit(contract, direct_vm, direct_bob)
    configure(direct_vm, SAFE)
    direct_vm.sender = direct_alice; contract.review("PX-001")
    direct_vm._llm_mocks.clear()
    direct_vm.mock_llm("PARALLAX-001", json.dumps(dict(SAFE, risk="yes")))
    assert direct_vm.run_validator(leader_result={"kind": "analysis", "result": dict(SAFE)}) is False
