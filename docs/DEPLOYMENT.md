# Deployment

## Current hardened v0.2.0 deployment

The final consensus-hardening source is deployed to Studionet and has been
verified byte-for-byte through `gen_getContractCode`.

- Contract: [`0x021b2ea7f5F907A6De41f3Ed468a29aFBAEB99D9`](https://explorer-studio.genlayer.com/address/0x021b2ea7f5F907A6De41f3Ed468a29aFBAEB99D9)
- Deployment transaction: [`0xf6481c518f4e5b80e929c77d4f7335550d723d93b6728643be068e67c84b9329`](https://explorer-studio.genlayer.com/tx/0xf6481c518f4e5b80e929c77d4f7335550d723d93b6728643be068e67c84b9329)
- Network/RPC: GenLayer Studionet (`https://studio.genlayer.com/api`)
- Source commit: `35acb34e7ca06a42da8f2c6ab01dda4bbef0d866`
- Source SHA-256: `8dd30617d217c3d3c35a1caf234e7758bd37a106ad36b4934d5af20c65a5a70c` (31,968 bytes)
- Deployment: `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`
- Source parity: decoded `gen_getContractCode` bytes equal the local source byte-for-byte (`YES`)
- Final `get_info()`: version `0.2.0`; `job_count=4`; `active_jobs=0`; `total_reward_deposited=0`; `total_worker_bonds_held=0`; `total_paid_to_workers=6000000000000`; `total_refunded_to_sponsors=2000000000000`.

### Live approved and blocked paths

- Approved path, job `PARALLAX-FINAL-HARDENED-1789428347502`: create [`0x854b1331...`](https://explorer-studio.genlayer.com/tx/0x854b1331ad1a94adbc463c069c682fc591ac955be2bcf5b6301efab708d01855), submit [`0x8881caa9...`](https://explorer-studio.genlayer.com/tx/0x8881caa939fda7a8d0c680101d7b5f358301f6f5ad52596108c05d40357b74a0), review [`0xed7536f1...`](https://explorer-studio.genlayer.com/tx/0xed7536f1339c68524dd071ca78e4727124339f5fac026702110a2785061312ce), settle [`0xff419c6f...`](https://explorer-studio.genlayer.com/tx/0xff419c6fcbb79d5b8db879d78e44def4635700920f7e2da36fa71cee4c870a09). All finalized with `MAJORITY_AGREE` and GenVM `SUCCESS`; review verdict `approved`, confidence `100`; final state `settled`, both ledgers zero. Worker payout transfer: [`0xa6144f54...`](https://explorer-studio.genlayer.com/tx/0xa6144f54574869640e20bd6d7bf7679c7ccc036d0264bad750352c987027e33d).
- Blocked path, job `PARALLAX-FINAL-HARDENED-1789428182687`: create [`0x5470e470...`](https://explorer-studio.genlayer.com/tx/0x5470e47081996f7528d1dee884bfd56a4b1034b8171baa1ebd689b588d0b8892), submit [`0x72587aab...`](https://explorer-studio.genlayer.com/tx/0x72587aab8d33ad3aecd5ed6f9791d7b52f75af5e88a1735c770694f4552958f9), review [`0x3e00e279...`](https://explorer-studio.genlayer.com/tx/0x3e00e2793b8772952d58a9f4f03cf319903062148d2b703788054222544676fb). The finalized review produced `blocked` at confidence `88`; settlement completed with zero reward and bond ledgers.

## Historical corrected deployment (superseded by the hardened source above)

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

## Full Studionet judgment lifecycle

This is separate from the event smoke job above and proves the complete
multimodal path on the same source-matched deployment.

- Job: `PARALLAX-FULL-LIFECYCLE-1789370871455`
- Sponsor: `0xF7FD246351268835Df39B1E8047fbCc4135E2B47`; worker: `0xaE82EFfe54dCcfd170d9a08EeE128339A70347f7`
- Reward/bond: `1000000000000` wei each; deadline `1789385271`
- Baseline URL/hash: `https://raw.githubusercontent.com/Bibidee/parallax/1315fc5f63841d15e0c1bd8edc0ff613b5ebc738/fixtures/lifecycle/baseline.txt` / `0x6452b1ee3499903c4bd839abbed23eec8c513b65a3d0d4853803b0047945db58`
- Target URL/hash: `https://raw.githubusercontent.com/Bibidee/parallax/1315fc5f63841d15e0c1bd8edc0ff613b5ebc738/fixtures/lifecycle/target.txt` / `0x0bb5e06101ce4c5b04bbc0e0efbe4abb47619122d11dd2ea27cfdc5ee699c305`
- Before image URL/hash: `https://cdn.jsdelivr.net/gh/Bibidee/parallax@1315fc5f63841d15e0c1bd8edc0ff613b5ebc738/fixtures/lifecycle/before.png` / `0xe47c8a5350f2f0cc3c694f97fe434c73246244092761912c878fc45a7b4184a5`
- After image URL/hash: `https://cdn.jsdelivr.net/gh/Bibidee/parallax@1315fc5f63841d15e0c1bd8edc0ff613b5ebc738/fixtures/lifecycle/after.png` / `0x01068fe46b24e05f1955e5f207345e9b8340cbf77743bfc1bfa8ef1b6a577176`
- Report URL/hash: `https://raw.githubusercontent.com/Bibidee/parallax/1315fc5f63841d15e0c1bd8edc0ff613b5ebc738/fixtures/lifecycle/report.txt` / `0xff63e273e01241c834d3bb1d7e8dcc557d1f7be21827f9b8f49fdaebeabf75b6`
- Create: [`0xeb2e4b5ea91722adf3db01319de6d42a0e11201136329d969d2345a0b605583f`](https://explorer-studio.genlayer.com/tx/0xeb2e4b5ea91722adf3db01319de6d42a0e11201136329d969d2345a0b605583f) — `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; state `pending`.
- Submit: [`0x78b9139fe551b4dd2d2c4cb99b28851c68635ffa8f85e00dfd0857ff9f319090`](https://explorer-studio.genlayer.com/tx/0x78b9139fe551b4dd2d2c4cb99b28851c68635ffa8f85e00dfd0857ff9f319090) — `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; state `submitted`, bond held `1000000000000` wei.
- Review: [`0xd7f6d8c5297016cbf057b972d0d931b21c1db8191f5bba39c93d2d82c14c4558`](https://explorer-studio.genlayer.com/tx/0xd7f6d8c5297016cbf057b972d0d931b21c1db8191f5bba39c93d2d82c14c4558) — `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; verdict `approved`, confidence `97`, one review attempt. The stored rationale states that the screenshots and worker report match the specified v1/PENDING → v2/COMPLETE change.
- Settlement: [`0xf19e74d4a95fdc0792fa426984fa2b1c22b4d82435c0e418c6bec5b32233a489`](https://explorer-studio.genlayer.com/tx/0xf19e74d4a95fdc0792fa426984fa2b1c22b4d82435c0e418c6bec5b32233a489) — `FINALIZED`, `MAJORITY_AGREE`, GenVM `SUCCESS`; outcome `approved`, sponsor `0`, worker `2000000000000` wei.
- Final state: `settled`, `reward_deposited=0`, `worker_bond_held=0`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`.

## Historical superseded deployment

Parallax v0.2.0 was previously deployed to Studionet at the address below. Its
source parity remains valid, but it is superseded and non-final because the
event topology caused the first payable call to fail at runtime. Do not reuse
this address for current evidence.

## Historical deployment evidence

- Contract: [`0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D`](https://explorer-studio.genlayer.com/address/0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D)
- Deployment transaction: [`0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e`](https://explorer-studio.genlayer.com/tx/0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e)
- Frozen commit: `b7be80e23e593e26db70245a862dde6dd763ce45`
- Source SHA-256: `ec96762ab1faa5334261abe0415f5ada37d15d39ceac9adf7b786248d3f86d1f` (31,457 bytes; `gen_getContractCode` parity: YES)
- Receipt: `FINALIZED`, `MAJORITY_AGREE`, GenVM deployment `SUCCESS`; deployer `0xF7FD246351268835Df39B1E8047fbCc4135E2B47`
- `get_info()`: version `0.2.0`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`
- Smoke test: [`0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85`](https://explorer-studio.genlayer.com/tx/0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85), finalized contract error at `JobCreated.emit()` (`SystemError: 2: inval`); no persistent state. This failure is retained as historical evidence and is not a result from the corrected source.

## Final release checklist (current hardened deployment)

- [x] exactly one deployable file under `contracts/`
- [x] `python scripts/preflight.py`
- [x] `python -m pytest tests -q` (25 passed)
- [x] `genvm-lint check contracts/parallax.py --json`
- [x] `genvm-lint schema contracts/parallax.py --output artifacts/parallax.abi.json`
- [x] source SHA-256 recorded before deployment
- [x] Studionet deployment FINALIZED with GenVM SUCCESS
- [x] `gen_getContractCode` source retrieved and compared byte-for-byte
- [x] `get_info()` matches version and configuration
- [x] live pending → cancelled smoke evidence recorded
- [x] live create → submit → review → approved → settle lifecycle recorded

The deployment above is retained for historical provenance only. The current
release is the hardened deployment at the top of this document.

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
