# Parallax design

Parallax combines a bounded multimodal observation with deterministic escrow. The sponsor's reward is custody; `reward_deposited` is the only ledger amount used by settlement. The designated worker's exact bond is tracked separately in `worker_bond_held`.

## Observation and consensus

Before nondeterministic execution, `review` copies all required job fields into an in-memory snapshot. The leader and each validator independently fetch baseline, target, report, and image bytes. Raw bytes are checked for HTTP status, role-specific size limits, exact SHA-256, and UTF-8 where text is required. The exact verified image bytes are passed directly to `exec_prompt(images=[...])`; there is no second URL render/fetch and therefore no image TOCTOU gap.

The model returns a bounded object: `spec_match`, `visual_change`, `evidence_support`, `evidence_quality`, `risk`, `confidence`, and `rationale`. Equivalence compares the deterministic derived verdict and, for blocked results, the bounded `fault_class`; rationale and confidence are explanatory. Approval still requires the complete safe tuple and confidence at least 75 in each observation. A disagreement that could change approval to blocked, or that changes payout-relevant fault attribution, is rejected by consensus. Technical/artifact and model failures are retryable and non-punitive; malformed outputs never approve.

## State machine

`pending -> submitted -> approved -> settled`

`submitted -> blocked -> settled`

`submitted -> retryable -> approved/blocked/retryable -> settled`

`pending -> cancelled`; `pending -> settled` through permissionless expiry at/after the deadline; `submitted -> approved/blocked/retryable`; `retryable -> approved/blocked/retryable`; `submitted/retryable -> settled` through permissionless `expire_job` at/after the deadline or exhausted attempts. Submission and review close at the exact deadline. A sponsor cannot cancel after evidence is bonded. Worker withdrawal is allowed only after a retryable timeout/attempt exhaustion, never while evidence is reviewable. A deadline gives every unresolved job a deterministic sponsor-reward/worker-bond refund route.

## Escrow safety

Every settlement reads the stored ledger, checks it is non-zero, sets both held ledgers to zero, saves the state, updates accounting counters, and only then calls the single GEN transfer helper. This ordering prevents replay and double payment. Settlement is permissionless so pause or an absent counterparty cannot strand funds.

`JobSettled` labels are explicit and bounded: `approved`, `semantic_blocked`, `retryable_refund`, `pending_cancel`, `expiry`, and `worker_withdrawal`. The label is selected from the pre-transition state, not inferred from payout direction. Payout addresses should be EOAs or GEN-capable recipients. `emit_transfer` is asynchronous: a finalized internal settlement does not guarantee acceptance by an arbitrary receiving contract, and no secondary recovery mechanism is implemented for a rejected child transfer.

## Event topology

GenVM supports at most three indexed (positional) event fields. Every Parallax
event stays within that bound. Stable identities and bounded status labels are
indexed; variable numeric metadata such as rewards, bonds, confidence, and
payout amounts is emitted in the event blob. This keeps event serialization
valid without dropping audit information. `tests/test_event_topology.py`
regresses both the declarations and all emission sites. Direct Mode executes
these emit call sites, but its in-process event shim does not reproduce the
deployed GenVM serializer; the historical deployment smoke transaction remains
the evidence that motivated a fresh deployment for runtime confirmation.

## Limits and assumptions

The contract supports textual artifacts and image URLs whose raw bytes can be fetched by GenLayer. Text artifacts are bounded at 16,000 bytes and image artifacts at 2,000,000 bytes. HTTPS hosts are syntactically validated and obvious private, loopback, link-local, multicast, and reserved IP literals (including ambiguous dotted forms) are rejected. External availability and validator consensus remain operational dependencies; uncertainty fails closed rather than fabricating approval.

## Economic fault classes

Substantive semantic rejection is the only punitive outcome: `blocked` settles reward and worker bond to the sponsor. Sponsor-provided artifact errors, worker-provided artifact integrity errors, HTTP/network failures, and model execution failures are recorded as retryable; expiry or retry exhaustion refunds the sponsor reward and worker bond to the worker. This prevents infrastructure controlled by the sponsor from silently slashing a worker. Every terminal path zeros both escrow ledgers before transfer and updates aggregate counters.

In the current API, `create_job` supplies baseline, target, before-image, and after-image commitments; `submit_evidence` supplies the worker report. Consequently, both image failures are classified as sponsor-artifact failures, while report failures are worker-artifact failures. Neither class is punitive by itself.
