from pathlib import Path
import ast
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sources = list((ROOT / "contracts").glob("*.py"))
if len(sources) != 1:
    raise SystemExit(f"expected exactly one deployable source, found {len(sources)}")
source = sources[0]
ast.parse(source.read_text(encoding="utf-8"))
subprocess.run([sys.executable, "-m", "pytest", "tests", "-q"], cwd=ROOT, check=True)
lint = shutil.which("genvm-lint") or shutil.which("genvm-lint.exe")
if not lint:
    sibling = Path(sys.executable).with_name("genvm-lint.exe" if sys.platform == "win32" else "genvm-lint")
    lint = str(sibling) if sibling.exists() else None
if not lint:
    raise SystemExit("genvm-lint is required for preflight")
subprocess.run([lint, "check", str(source), "--json"], cwd=ROOT, check=True)
(ROOT / "artifacts").mkdir(exist_ok=True)
subprocess.run([lint, "schema", str(source), "--output", "artifacts/parallax.abi.json"], cwd=ROOT, check=True)
print("preflight passed")
