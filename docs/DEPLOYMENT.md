# Deployment

Parallax v0.1.0 is currently **undeployed**. No contract address or live transaction is claimed. The source must remain frozen only after the complete release gate passes.

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

If any gate fails, preserve the failure output, fix the underlying issue, and rerun the entire gate. Never replace a failed check with a skipped test or an aspirational claim.
