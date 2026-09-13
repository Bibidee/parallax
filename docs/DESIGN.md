# Parallax design

Parallax combines a bounded multimodal observation with deterministic escrow. The sponsor's reward is custody; `reward_deposited` is the only ledger amount used by settlement. The designated worker's exact bond is tracked separately in `worker_bond_held`.

## Observation and consensus

Before nondeterministic execution, `review` copies all required job fields into an in-memory snapshot. The leader and each validator independently fetch baseline, target, report, and image bytes. Raw bytes are checked for HTTP status, size, exact SHA-256, and UTF-8 where text is required. Images are additionally rendered as screenshots and passed to the semantic model.

The model returns a bounded object: `spec_match`, `visual_change`, `evidence_support`, `evidence_quality`, `risk`, `confidence`, and `rationale`. Equivalence compares the deterministic derived verdict: approval still requires the complete safe tuple and confidence at least 75 in each observation, while two valid blocked observations may differ in their blocking dimensions or rationale because neither can authorize a payout. Any disagreement that could change approval to blocked is rejected by consensus. Technical fetch and model failures are retryable; malformed outputs never approve.

## State machine

`pending -> submitted -> approved -> settled`

`submitted -> blocked -> settled`

`submitted -> retryable -> approved/blocked/retryable -> settled`

`pending -> cancelled`; `submitted/retryable -> cancelled` through worker withdrawal. A sponsor cannot cancel after evidence is bonded. A deadline gives retryable jobs a deterministic sponsor-refund/worker-bond-refund route.

## Escrow safety

Every settlement reads the stored ledger, checks it is non-zero, sets both held ledgers to zero, saves the state, updates accounting counters, and only then calls the single GEN transfer helper. This ordering prevents replay and double payment. Settlement is permissionless so pause or an absent counterparty cannot strand funds.

## Limits and assumptions

The contract supports textual artifacts and image URLs whose raw bytes can be fetched by GenLayer. HTTPS hosts are syntactically validated and obvious private, loopback, link-local, multicast, and reserved IP literals are rejected. External availability and validator consensus remain operational dependencies; uncertainty fails closed rather than fabricating approval.
