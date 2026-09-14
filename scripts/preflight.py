from pathlib import Path
import ast
import hashlib
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sources = list((ROOT / "contracts").glob("*.py"))
if len(sources) != 1:
    raise SystemExit(f"expected exactly one deployable source, found {len(sources)}")
source = sources[0]
source_bytes = source.read_bytes()
ast.parse(source_bytes.decode("utf-8"))
print(f"contract_sha256={hashlib.sha256(source_bytes).hexdigest()}")
subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=ROOT, check=True)
lint = shutil.which("genvm-lint") or shutil.which("genvm-lint.exe")
if not lint:
    executable = "genvm-lint.exe" if sys.platform == "win32" else "genvm-lint"
    candidates = (
        Path(sys.executable).with_name(executable),
        Path(sys.executable).parent / "Scripts" / executable,
    )
    lint = next((str(candidate) for candidate in candidates if candidate.exists()), None)
if not lint:
    raise SystemExit("genvm-lint is required for preflight")
subprocess.run([lint, "check", str(source), "--json"], cwd=ROOT, check=True)
(ROOT / "artifacts").mkdir(exist_ok=True)
subprocess.run([lint, "schema", str(source), "--output", "artifacts/parallax.abi.json"], cwd=ROOT, check=True)
print("preflight passed")
