# Parallax v0.1.0

Parallax is a standalone GenLayer Intelligent Contract primitive for multimodal milestone escrow. A sponsor commits the exact text and image artifacts that define a before/after state, funds a reward in GEN, and designates a worker. The worker submits a hash-bound completion report and a small bond. GenLayer validators independently fetch the committed bytes, verify SHA-256 and UTF-8 integrity, render the before/after images, and semantically assess whether the requested state change is proven.

## Why GenLayer

Ordinary contracts can hold GEN and compare hashes, but cannot independently interpret whether two photographs show the requested change or whether a report supports a specification. Parallax uses `run_nondet_unsafe` so multiple validators perform the observation themselves. Deterministic contract code alone derives the authorization outcome, enforces the designated worker, and settles escrow exactly once. No single model, trusted oracle, or frontend can authorize a payout.

Artifacts are hostile quoted data: instructions inside them are never followed. Every fetched byte is bounded and hashed before semantic review. Any unavailable source, HTTP failure, mismatch, invalid UTF-8, malformed model result, or validator disagreement fails closed or remains retryable.

## Lifecycle

`create_job` is payable and records the sponsor's reward ledger. `submit_evidence` is payable and requires the exact worker bond from the designated worker. A permitted sponsor or worker calls `review`; validators independently inspect the snapshot. A complete safe tuple (`spec_match=yes`, `visual_change=yes`, `evidence_support=yes`, `evidence_quality=strong|adequate`, `risk=no`, confidence >= 75) becomes `approved`; all other valid semantic outcomes become `blocked`. Technical fetch/model failures become `retryable`.

Settlement has a closed set of exits:

- approved: worker receives reward plus bond;
- blocked: sponsor receives reward plus bond;
- retryable after the deadline: sponsor receives reward and the worker bond is refunded;
- sponsor cancellation before evidence: sponsor receives the reward;
- worker withdrawal before final review: worker receives the bond.

Each payout zeros the corresponding ledger fields and persists state before emitting GEN. A second settlement therefore has no balance to release. The deadline also prevents an unresolved review from stranding funds forever.

## Integration example

Another Intelligent Contract can use Parallax as an authorization gate by reading `get_job(job_id)`, requiring `status == "approved"`, and requiring the caller to equal the stored `worker` before invoking `consume`-like downstream behavior. Parallax's `settle` should then be called once to release the escrow. Downstream code must still validate its own business rules; an approved semantic review is evidence of the committed milestone, not a universal truth oracle.

## Release gate

This repository intentionally contains exactly one deployable source: `contracts/parallax.py`. Run `python scripts/preflight.py` to parse it, run all tests, run GenVM lint, and generate the ABI schema. The current package is undeployed; deployment evidence will be added only after a frozen source, finalized Studionet receipt, and byte-for-byte source retrieval are available.

The official GenLayer development and validator guidance is available at [skills.genlayer.com](https://skills.genlayer.com/).
