# Parallax v0.2.0

Parallax is a standalone GenLayer Intelligent Contract primitive for multimodal milestone escrow. A sponsor commits exact text and image artifacts describing a before/after state, funds a reward in GEN, and designates a worker. The worker submits a hash-bound completion report and a bond. Validators independently fetch and hash every artifact; the exact verified image bytes are passed directly to a multimodal model, so the model never reviews a second URL fetch.

## Why GenLayer

Ordinary contracts can hold GEN and compare hashes, but cannot independently interpret whether photographs show the requested change or whether a report supports a specification. `run_nondet_unsafe` lets multiple validators perform the observation themselves. Deterministic code derives the authorization outcome, enforces the designated worker, and settles escrow exactly once. Artifacts are hostile quoted data: embedded instructions are never followed.

Approval requires the complete safe tuple (`spec_match=yes`, `visual_change=yes`, `evidence_support=yes`, `evidence_quality=strong|adequate`, `risk=no`, confidence >= 75) from consensus. Validators must also agree exactly on all five material semantic fields; rationale may differ, and confidence may differ only when both scores are on the same side of the 75-point approval threshold. Material disagreement is rejected and cannot slash the worker bond. Semantic rejection is `blocked`; artifact, network, or model failures are non-punitive `retryable` outcomes. Both before and after image commitments are sponsor-provided; the worker owns only the submitted report. Malformed output never approves.

## Lifecycle

`create_job` is payable and records the sponsor's reward ledger. `submit_evidence` is payable and requires the exact worker bond from the designated worker. A permitted sponsor or worker calls `review`; validators independently inspect the snapshot. A complete safe tuple (`spec_match=yes`, `visual_change=yes`, `evidence_support=yes`, `evidence_quality=strong|adequate`, `risk=no`, confidence >= 75) becomes `approved`; all other valid semantic outcomes become `blocked`. Technical fetch/model failures become `retryable`.

The normal state paths are `pending -> submitted -> approved|blocked|retryable -> settled`; a sponsor may cancel only `pending` before evidence is bonded. Any unresolved `pending`, `submitted`, or `retryable` job has a permissionless `expire_job` path at/after its deadline (or exhausted attempts), which settles the escrow without approval.

Settlement has a closed set of exits:

- approved: worker receives reward plus bond;
- substantive semantic blocked: sponsor receives reward plus bond;
- sponsor/worker artifact or infrastructure failure: retryable; after the deadline both owners are refunded;
- retryable after deadline or exhausted attempts: permissionless `expire_job` refunds sponsor reward and worker bond;
- sponsor cancellation before evidence: sponsor receives the reward;
- worker withdrawal is forbidden while evidence is reviewable and is available only after retryable timeout/attempt exhaustion.

All payout paths zero both ledgers, persist state, update accounting, and only then emit GEN. A second settle/expire/withdraw has no balance to release. `MAX_ACTIVE_JOBS` bounds live storage pressure while finalized records remain auditable; `job_count` is informational, not a lifetime admission cap.

`JobSettled` uses explicit outcomes: `approved`, `semantic_blocked`, `retryable_refund`, `pending_cancel`, `expiry`, and `worker_withdrawal`. These labels describe the state transition and are never inferred from which party happens to receive funds.

Payout recipients should be EOAs or contracts that can receive GEN. Parallax zeroes its escrow ledgers before calling asynchronous `emit_transfer`, but settlement finalization does not guarantee that an arbitrary receiving contract accepts the downstream child transfer. Failed child-transfer behavior follows GenLayer runtime semantics; Parallax has no secondary recovery mechanism for a recipient contract that rejects a transfer.

## Integration example

Another Intelligent Contract can use Parallax as an authorization gate by reading `get_job(job_id)`, requiring `status == "approved"`, and requiring the caller to equal the stored `worker` before invoking `consume`-like downstream behavior. Parallax's `settle` should then be called once to release the escrow. Downstream code must still validate its own business rules; an approved semantic review is evidence of the committed milestone, not a universal truth oracle.

## Release gate

This repository intentionally contains exactly one deployable source: `contracts/parallax.py`. Run `python scripts/preflight.py` to parse it, run all tests, run GenVM lint, and generate the ABI schema. The corrected v0.2.0 source is now deployed to Studionet with byte-for-byte parity and a successful payable create/cancel smoke path. The earlier deployment remains historical evidence of the event-topic incompatibility.

## Historical Studionet deployment evidence

- Contract: [`0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D`](https://explorer-studio.genlayer.com/address/0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D)
- Deployment transaction: [`0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e`](https://explorer-studio.genlayer.com/tx/0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e)
- Network: GenLayer Studionet (`https://studio.genlayer.com/api`); deployer `0xF7FD246351268835Df39B1e8047fbCc4135E2B47`
- Frozen source commit: `b7be80e23e593e26db70245a862dde6dd763ce45`
- Local/deployed SHA-256: `ec96762ab1faa5334261abe0415f5ada37d15d39ceac9adf7b786248d3f86d1f` (31,457 bytes each; parity verified through `gen_getContractCode`)
- Deployment receipt: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; `get_info()` returns Parallax `0.2.0` with zero active jobs and zero held ledgers.
- Smoke-test transaction: [`0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85`](https://explorer-studio.genlayer.com/tx/0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85). It finalized with `MAJORITY_AGREE`, but GenVM executions errored at `JobCreated.emit()` (`SystemError: 2: inval`); `PARALLAX-SMOKE-001` was not persisted and accounting remained zero. This is retained solely as historical evidence for the superseded deployment.

## Corrected Studionet deployment

- Contract: [`0x27CdC3c266F9b8402Ac4723AA0c1A28D77C7B8a9`](https://explorer-studio.genlayer.com/address/0x27CdC3c266F9b8402Ac4723AA0c1A28D77C7B8a9)
- Deployment transaction: [`0x267e6479907a5066c1e49da30dee2f9a7655d08b93775962042f78c4561d8481`](https://explorer-studio.genlayer.com/tx/0x267e6479907a5066c1e49da30dee2f9a7655d08b93775962042f78c4561d8481)
- Network: GenLayer Studionet (`https://studio.genlayer.com/api`); deployer `0xF7FD246351268835Df39B1e8047fbCc4135E2B47`
- Frozen commit: `8e200e2ab1d300090e5c048b4d13121ccd343d98`; source SHA-256 `08a3a39f38d95949edff045905efa56d9e7332605881dd48969c6c1ead26dbc9` (31,588 bytes)
- Deployment: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; `gen_getContractCode` parity is byte-for-byte verified.
- Initial `get_info()`: version `0.2.0`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`.
- Event smoke create: [`0xe296422fa9d45ce2a8a4e18c027238dd999e84a8986b6a5c529b18dd6e9f68fa`](https://explorer-studio.genlayer.com/tx/0xe296422fa9d45ce2a8a4e18c027238dd999e84a8986b6a5c529b18dd6e9f68fa), `FINALIZED`/`MAJORITY_AGREE`/GenVM `SUCCESS`; `PARALLAX-EVENT-SMOKE-002` persisted as `pending` with reward `1000000000000` wei and no event serialization error.
- Pending cancellation: [`0x5b441d0a43741dcc14cf01ea02bcb9333669acf8f5304c38ea4fcedd101dcb42`](https://explorer-studio.genlayer.com/tx/0x5b441d0a43741dcc14cf01ea02bcb9333669acf8f5304c38ea4fcedd101dcb42), `FINALIZED`/`MAJORITY_AGREE`/GenVM `SUCCESS`; status `cancelled`, reward ledger `0`, and `active_jobs=0`.
- Final `get_info()`: `job_count=1`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`, `total_refunded_to_sponsors=1000000000000`. The Explorer receipt exposes a successful non-removed EVM log, while symbolic event names/blob fields are not surfaced by the available receipt view.

### Full Studionet judgment lifecycle

The corrected deployment also completed a real multimodal escrow lifecycle (distinct from the pending/cancel event smoke test):

- Job `PARALLAX-FULL-LIFECYCLE-1789370871455`; sponsor `0xF7FD246351268835Df39B1e8047fbCc4135E2B47`; worker/designated payout recipient `0xaE82EFfe54dCcfd170d9a08EeE128339A70347f7`.
- Specification: approve only when verified evidence shows the dashboard changed from `PARALLAX DEMO v1`/`PENDING` to `PARALLAX DEMO v2`/`COMPLETE`.
- Reward and worker bond: `1000000000000` wei each; deadline `1789385271`.
- Immutable artifacts (raw-byte SHA-256): baseline `0x6452b1ee3499903c4bd839abbed23eec8c513b65a3d0d4853803b0047945db58`; target `0x0bb5e06101ce4c5b04bbc0e0efbe4abb47619122d11dd2ea27cfdc5ee699c305`; before image `0xe47c8a5350f2f0cc3c694f97fe434c73246244092761912c878fc45a7b4184a5`; after image `0x01068fe46b24e05f1955e5f207345e9b8340cbf77743bfc1bfa8ef1b6a577176`; report `0xff63e273e01241c834d3bb1d7e8dcc557d1f7be21827f9b8f49fdaebeabf75b6`.
- `create_job`: [`0xeb2e4b5ea91722adf3db01319de6d42a0e11201136329d969d2345a0b605583f`](https://explorer-studio.genlayer.com/tx/0xeb2e4b5ea91722adf3db01319de6d42a0e11201136329d969d2345a0b605583f), `FINALIZED`/`MAJORITY_AGREE`/GenVM `SUCCESS`; read-back `pending` with reward deposited and no bond held.
- `submit_evidence`: [`0x78b9139fe551b4dd2d2c4cb99b28851c68635ffa8f85e00dfd0857ff9f319090`](https://explorer-studio.genlayer.com/tx/0x78b9139fe551b4dd2d2c4cb99b28851c68635ffa8f85e00dfd0857ff9f319090), `FINALIZED`/`MAJORITY_AGREE`/GenVM `SUCCESS`; read-back `submitted` with the exact report hash and bond held.
- `review`: [`0xd7f6d8c5297016cbf057b972d0d931b21c1db8191f5bba39c93d2d82c14c4558`](https://explorer-studio.genlayer.com/tx/0xd7f6d8c5297016cbf057b972d0d931b21c1db8191f5bba39c93d2d82c14c4558), `FINALIZED`/`MAJORITY_AGREE`/GenVM `SUCCESS`; verdict `approved`, confidence `97`, one review attempt. Stored rationale: “The specification requires changing the dashboard from PARALLAX DEMO v1 with PENDING to PARALLAX DEMO v2 with COMPLETE. The screenshots clearly show this exact before/after change, and the worker report matches the requested state.”
- `settle`: [`0xf19e74d4a95fdc0792fa426984fa2b1c22b4d82435c0e418c6bec5b32233a489`](https://explorer-studio.genlayer.com/tx/0xf19e74d4a95fdc0792fa426984fa2b1c22b4d82435c0e418c6bec5b32233a489), `FINALIZED`/`MAJORITY_AGREE`/GenVM `SUCCESS`; outcome `approved`, sponsor payout `0`, worker payout `2000000000000` wei. Final read-back: `settled`, `reward_deposited=0`, `worker_bond_held=0`, `active_jobs=0`.

The official GenLayer development and validator guidance is available at [skills.genlayer.com](https://skills.genlayer.com/).
