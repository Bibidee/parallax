# Deployment

Parallax v0.2.0 is deployed to Studionet, with byte-for-byte source parity verified, but the deployment is **not smoke-test verified**. The first payable `create_job` call finalized with `MAJORITY_AGREE` while all executions failed at `JobCreated.emit()` with `SystemError: 2: inval`; no job state persisted. Do not treat this deployment as production-ready until that runtime incompatibility is fixed in a new audited source.

## Current deployment evidence

- Contract: [`0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D`](https://explorer-studio.genlayer.com/address/0xB5a6a8F4161CC77D24ffe2cD044B95aD41c9fb2D)
- Deployment transaction: [`0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e`](https://explorer-studio.genlayer.com/tx/0x535f764500aa5b0f1b86ac08d30e011874ab32979c4b931a213d880e0301a20e)
- Frozen commit: `b7be80e23e593e26db70245a862dde6dd763ce45`
- Source SHA-256: `ec96762ab1faa5334261abe0415f5ada37d15d39ceac9adf7b786248d3f86d1f` (31,457 bytes; `gen_getContractCode` parity: YES)
- Receipt: `FINALIZED`, `MAJORITY_AGREE`, GenVM deployment `SUCCESS`; deployer `0xF7FD246351268835Df39B1E8047fbCc4135E2B47`
- `get_info()`: version `0.2.0`, `active_jobs=0`, `total_reward_deposited=0`, `total_worker_bonds_held=0`
- Smoke test: [`0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85`](https://explorer-studio.genlayer.com/tx/0x570a406cea443dd148cedf8af3db335392355e711a3e6c969b386719ed89ab85), finalized contract error at `JobCreated.emit()` (`SystemError: 2: inval`); no persistent state.

## Release checklist

- [ ] exactly one deployable file under `contracts/`
- [ ] `python scripts/preflight.py`
- [ ] `python -m pytest tests -q`
- [ ] `genvm-lint check contracts/parallax.py --json`
- [ ] `genvm-lint schema contracts/parallax.py --output artifacts/parallax.abi.json`
- [ ] source SHA-256 recorded before deployment
- [x] Studionet deployment FINALIZED with GenVM SUCCESS
- [x] `gen_getContractCode` source retrieved and compared byte-for-byte
- [x] `get_info()` matches version and configuration
- [ ] live pending → approved/blocked → settled evidence recorded (blocked by the `JobCreated.emit()` runtime error above)

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
