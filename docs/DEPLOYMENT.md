# Deployment

Parallax v0.2.0 is currently **undeployed**. No contract address or live transaction is claimed. The source must remain frozen only after the complete release gate passes.

## Release checklist

- [ ] exactly one deployable file under `contracts/`
- [ ] `python scripts/preflight.py`
- [ ] `python -m pytest tests -q`
- [ ] `genvm-lint check contracts/parallax.py --json`
- [ ] `genvm-lint schema contracts/parallax.py --output artifacts/parallax.abi.json`
- [ ] source SHA-256 recorded before deployment
- [ ] Studionet deployment FINALIZED with GenVM SUCCESS
- [ ] `gen_getContractCode` source retrieved and compared byte-for-byte
- [ ] `get_info()` matches version and configuration
- [ ] live pending → approved/blocked → settled evidence recorded

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
