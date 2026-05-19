from __future__ import annotations

import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, cwd=ROOT, check=True)


def copy_fixture(tmp_path: Path) -> Path:
    experiment_dir = tmp_path / "stroop"
    experiment_dir.mkdir()
    shutil.copy(ROOT / "tests" / "fixtures" / "stroop" / "experiment_spec.yaml", experiment_dir / "experiment_spec.yaml")
    return experiment_dir / "experiment_spec.yaml"


class PipelineTests(unittest.TestCase):
    def test_psychopy_pipeline(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            spec = copy_fixture(Path(tmp))
            run([sys.executable, "scripts/run_pipeline.py", str(spec), "--platform", "psychopy"])

            report = spec.parent / "psychopy" / "validation_report.md"
            code = spec.parent / "psychopy" / "run_experiment.py"
            self.assertTrue(code.exists())
            self.assertIn("Result: `28/28` checks passed", report.read_text(encoding="utf-8"))
            self.assertIn("duration_frames", code.read_text(encoding="utf-8"))

    def test_psychtoolbox_pipeline(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            spec = copy_fixture(Path(tmp))
            run([sys.executable, "scripts/run_pipeline.py", str(spec), "--platform", "psychtoolbox"])

            report = spec.parent / "psychtoolbox" / "validation_report.md"
            code = spec.parent / "psychtoolbox" / "stroop_color_word.m"
            self.assertTrue(code.exists())
            self.assertIn("Result: `29/29` checks passed", report.read_text(encoding="utf-8"))
            text = code.read_text(encoding="utf-8")
            self.assertIn("durationFrames", text)
            self.assertIn("Screen('Preference', 'SkipSyncTests', 0)", text)


if __name__ == "__main__":
    unittest.main()
