# Parallax v0.2.0

Parallax is a standalone GenLayer Intelligent Contract primitive for multimodal milestone escrow. A sponsor commits exact text and image artifacts describing a before/after state, funds a reward in GEN, and designates a worker. The worker submits a hash-bound completion report and a bond. Validators independently fetch and hash every artifact; the exact verified image bytes are passed directly to a multimodal model, so the model never reviews a second URL fetch.

## Why GenLayer

Ordinary contracts can hold GEN and compare hashes, but cannot independently interpret whether photographs show the requested change or whether a report supports a specification. `run_nondet_unsafe` lets multiple validators perform the observation themselves. Deterministic code derives the authorization outcome, enforces the designated worker, and settles escrow exactly once. Artifacts are hostile quoted data: embedded instructions are never followed.

Approval requires the complete safe tuple (`spec_match=yes`, `visual_change=yes`, `evidence_support=yes`, `evidence_quality=strong|adequate`, `risk=no`, confidence >= 75) from consensus. Semantic rejection is `blocked`; artifact, network, or model failures are non-punitive `retryable` outcomes. Both before and after image commitments are sponsor-provided; the worker owns only the submitted report. Malformed output never approves.

## Lifecycle

`create_job` is payable and records the sponsor's reward ledger. `submit_evidence` is payable and requires the exact worker bond from the designated worker. A permitted sponsor or worker calls `review`; validators independently inspect the snapshot. A complete safe tuple (`spec_match=yes`, `visual_change=yes`, `evidence_support=yes`, `evidence_quality=strong|adequate`, `risk=no`, confidence >= 75) becomes `approved`; all other valid semantic outcomes become `blocked`. Technical fetch/model failures become `retryable`.

Settlement has a closed set of exits:

- approved: worker receives reward plus bond;
- substantive semantic blocked: sponsor receives reward plus bond;
- sponsor/worker artifact or infrastructure failure: retryable; after the deadline both owners are refunded;
- retryable after deadline or exhausted attempts: permissionless `expire_job` refunds sponsor reward and worker bond;
- sponsor cancellation before evidence: sponsor receives the reward;
- worker withdrawal is forbidden while evidence is reviewable and is available only after retryable timeout/attempt exhaustion.

All payout paths zero both ledgers, persist state, update accounting, and only then emit GEN. A second settle/expire/withdraw has no balance to release. `MAX_ACTIVE_JOBS` bounds live storage pressure while finalized records remain auditable; `job_count` is informational, not a lifetime admission cap.

## Integration example

Another Intelligent Contract can use Parallax as an authorization gate by reading `get_job(job_id)`, requiring `status == "approved"`, and requiring the caller to equal the stored `worker` before invoking `consume`-like downstream behavior. Parallax's `settle` should then be called once to release the escrow. Downstream code must still validate its own business rules; an approved semantic review is evidence of the committed milestone, not a universal truth oracle.

## Release gate

This repository intentionally contains exactly one deployable source: `contracts/parallax.py`. Run `python scripts/preflight.py` to parse it, run all tests, run GenVM lint, and generate the ABI schema. The current package is undeployed; deployment evidence will be added only after a frozen source, finalized Studionet receipt, and byte-for-byte source retrieval are available.

The official GenLayer development and validator guidance is available at [skills.genlayer.com](https://skills.genlayer.com/).
