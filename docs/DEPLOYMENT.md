# Deployment

## Corrected v0.2.0 deployment (current)

The bounded-event source is deployed and smoke-tested on Studionet. Every
deployment and smoke transaction below finalized with `MAJORITY_AGREE` and
GenVM `SUCCESS`.

- Contract: [`0x27CdC3c266F9b8402Ac4723AA0c1A28D77C7B8a9`](https://explorer-studio.genlayer.com/address/0x27CdC3c266F9b8402Ac4723AA0c1A28D77C7B8a9)
- Deployment transaction: [`0x267e6479907a5066c1e49da30dee2f9a7655d08b93775962042f78c4561d8481`](https://explorer-studio.genlayer.com/tx/0x267e6479907a5066c1e49da30dee2f9a7655d08b93775962042f78c4561d8481)
- Network/RPC: GenLayer Studionet (`https://studio.genlayer.com/api`)
- Deployer: `0xF7FD246351268835Df39B1E8047fbCc4135E2B47`
- Source commit: `8e200e2ab1d300090e5c048b4d13121ccd343d98`
- Source SHA-256: `08a3a39f38d95949edff045905efa56d9e7332605881dd48969c6c1ead26dbc9` (31,588 bytes)
- Source parity: `gen_getContractCode` decoded bytes match the repository byte-for-byte (`YES`)
- Initial `get_info()`: version `0.2.0`; `active_jobs=0`; `total_reward_deposited=0`; `total_worker_bonds_held=0`
- Event smoke create: [`0xe296422fa9d45ce2a8a4e18c027238dd999e84a8986b6a5c529b18dd6e9f68fa`](https://explorer-studio.genlayer.com/tx/0xe296422fa9d45ce2a8a4e18c027238dd999e84a8986b6a5c529b18dd6e9f68fa). `PARALLAX-EVENT-SMOKE-002` was created successfully as `pending` with reward `1000000000000` wei; no `JobCreated` serialization error occurred.
- Cancellation: [`0x5b441d0a43741dcc14cf01ea02bcb9333669acf8f5304c38ea4fcedd101dcb42`](https://explorer-studio.genlayer.com/tx/0x5b441d0a43741dcc14cf01ea02bcb9333669acf8f5304c38ea4fcedd101dcb42). The job became `cancelled`, reward ledger returned to `0`, and no `JobSettled` serialization error occurred.
- Final `get_info()`: `job_count=1`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`, `total_refunded_to_sponsors=1000000000000`.
- The available EVM receipt view exposes a successful non-removed log but does not decode symbolic event names/blob fields; runtime success is the live event-path confirmation.

## Historical superseded deployment

Parallax v0.2.0 was previously deployed to Studionet at the address below. Its
source parity remains valid, but it is superseded and non-final because the
event topology caused the first payable call to fail at runtime. Do not reuse
this address for current evidence.

## Current deployment evidence

- Contract: [`0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D`](https://explorer-studio.genlayer.com/address/0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D)
- Deployment transaction: [`0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e`](https://explorer-studio.genlayer.com/tx/0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e)
- Frozen commit: `b7be80e23e593e26db70245a862dde6dd763ce45`
- Source SHA-256: `ec96762ab1faa5334261abe0415f5ada37d15d39ceac9adf7b786248d3f86d1f` (31,457 bytes; `gen_getContractCode` parity: YES)
- Receipt: `FINALIZED`, `MAJORITY_AGREE`, GenVM deployment `SUCCESS`; deployer `0xF7FD246351268835Df39B1E8047fbCc4135E2B47`
- `get_info()`: version `0.2.0`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`
- Smoke test: [`0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85`](https://explorer-studio.genlayer.com/tx/0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85), finalized contract error at `JobCreated.emit()` (`SystemError: 2: inval`); no persistent state. This failure is retained as historical evidence and is not a result from the corrected source.

## Release checklist

- [x] exactly one deployable file under `contracts/`
- [x] `python scripts/preflight.py`
- [x] `python -m pytest tests -q` (24 passed)
- [x] `genvm-lint check contracts/parallax.py --json`
- [x] `genvm-lint schema contracts/parallax.py --output artifacts/parallax.abi.json`
- [x] source SHA-256 recorded before deployment
- [x] Studionet deployment FINALIZED with GenVM SUCCESS
- [x] `gen_getContractCode` source retrieved and compared byte-for-byte
- [x] `get_info()` matches version and configuration
- [x] live pending → cancelled smoke evidence recorded on the corrected deployment

The corrected deployment above is the current release candidate. A broader
multimodal review/settlement flow remains optional evidence; the required
event-topology create/cancel smoke path is finalized and successful.

## Economic safety checks

- Sponsor artifact, worker artifact, HTTP, and model failures are retryable and non-punitive.
- `create_job` supplies both image commitments; `submit_evidence` supplies the worker report, so image failures are sponsor-artifact failures.
- Only a substantive semantic `blocked` result transfers the worker bond to the sponsor.
- `expire_job` is permissionless after the deadline or exhausted review attempts and refunds both owners.
- `withdraw_evidence` cannot run while evidence is reviewable; it is a timeout recovery path only.
- Before/after image hashes must differ, and the exact verified raw image bytes are passed to the multimodal model.
- `MAX_ACTIVE_JOBS` is an active-capacity bound; finalized historical jobs remain readable and do not consume active capacity.
- Payout recipients should be EOAs or GEN-capable contracts. `emit_transfer` is asynchronous; internal settlement finalization does not guarantee arbitrary recipient acceptance, and Parallax has no secondary recovery path for a rejected child transfer.
- `JobSettled` outcomes are explicit: `approved`, `semantic_blocked`, `retryable_refund`, `pending_cancel`, `expiry`, and `worker_withdrawal`.

If any gate fails, preserve the failure output, fix the underlying issue, and rerun the entire gate. Never replace a failed check with a skipped test or an aspirational claim.
