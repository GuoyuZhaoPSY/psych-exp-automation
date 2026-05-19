#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable


sys.path.insert(0, str(ROOT / "scripts"))
from common import read_spec  # noqa: E402


def run(cmd: list[str]) -> None:
    print("$ " + " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--platform", choices=["psychopy", "psychtoolbox"], default=None)
    parser.add_argument("--out-root", type=Path, default=None)
    args = parser.parse_args()

    spec_path = args.spec.resolve()
    spec = read_spec(spec_path)
    run([PY, "scripts/validate_spec.py", str(spec_path)])

    # Read the default platform lazily by letting generate_code choose unless overridden.
    platform_args = []
    if args.platform:
        platform_args = ["--platform", args.platform]
        platform = args.platform
    else:
        platform = spec["target_platform"]["default"]

    out_root = args.out_root.resolve() if args.out_root else spec_path.parent

    pseudo = out_root / "pseudocode.md"
    run([PY, "scripts/render_pseudocode.py", str(spec_path), "--out", str(pseudo)])

    code_out = out_root / platform
    run([PY, "scripts/generate_code.py", str(spec_path), *platform_args, "--out", str(code_out)])

    experiment_id = re.sub(r"[^0-9a-zA-Z_]+", "_", spec["metadata"]["experiment_id"])
    code_path = code_out / ("run_experiment.py" if platform == "psychopy" else f"{experiment_id}.m")
    report = code_out / "validation_report.md"
    run([PY, "scripts/validate_generated_code.py", str(spec_path), str(code_path), "--platform", platform, "--report", str(report)])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
