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

    def test_reverse_psychopy_snapshot(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            spec = copy_fixture(Path(tmp))
            run([sys.executable, "scripts/run_pipeline.py", str(spec), "--platform", "psychopy"])
            run([sys.executable, "scripts/reverse_engineer.py", str(spec.parent / "psychopy" / "run_experiment.py")])

            reverse = spec.parent / "reverse"
            self.assertTrue((reverse / "reversed_experiment_spec.yaml").exists())
            self.assertIn("Confidence: `high`", (reverse / "reverse_report.md").read_text(encoding="utf-8"))
            self.assertIn("颜色-词 Stroop 任务", (reverse / "design_description.md").read_text(encoding="utf-8"))

    def test_reverse_psychtoolbox_snapshot(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            spec = copy_fixture(Path(tmp))
            run([sys.executable, "scripts/run_pipeline.py", str(spec), "--platform", "psychtoolbox"])
            run([sys.executable, "scripts/reverse_engineer.py", str(spec.parent / "psychtoolbox" / "stroop_color_word.m")])

            reverse = spec.parent / "reverse"
            self.assertTrue((reverse / "reversed_experiment_spec.yaml").exists())
            self.assertIn("Confidence: `high`", (reverse / "reverse_report.md").read_text(encoding="utf-8"))

    def test_reverse_generated_psychopy_constants_without_snapshot(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            spec = copy_fixture(Path(tmp))
            run([sys.executable, "scripts/run_pipeline.py", str(spec), "--platform", "psychopy"])
            (spec.parent / "psychopy" / "experiment_spec.snapshot.json").unlink()
            run([sys.executable, "scripts/reverse_engineer.py", str(spec.parent / "psychopy" / "run_experiment.py")])

            text = (spec.parent / "reverse" / "reversed_experiment_spec.yaml").read_text(encoding="utf-8")
            self.assertIn("stroop_color_word", text)
            self.assertIn("TRIAL", (spec.parent / "reverse" / "reverse_report.md").read_text(encoding="utf-8").upper())

    def test_reverse_generated_psychtoolbox_variables_without_snapshot(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            spec = copy_fixture(Path(tmp))
            run([sys.executable, "scripts/run_pipeline.py", str(spec), "--platform", "psychtoolbox"])
            (spec.parent / "psychtoolbox" / "experiment_spec.snapshot.json").unlink()
            run([sys.executable, "scripts/reverse_engineer.py", str(spec.parent / "psychtoolbox" / "stroop_color_word.m")])

            text = (spec.parent / "reverse" / "reversed_experiment_spec.yaml").read_text(encoding="utf-8")
            self.assertIn("stroop_color_word", text)
            self.assertIn("Psychtoolbox", (spec.parent / "reverse" / "reverse_report.md").read_text(encoding="utf-8"))

    def test_reverse_handwritten_psychopy(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "handwritten"
            folder.mkdir()
            code = folder / "psychopy_task.py"
            shutil.copy(ROOT / "tests" / "fixtures" / "handwritten" / "psychopy_task.py", code)
            run([sys.executable, "scripts/reverse_engineer.py", str(code)])

            report = (folder / "reverse" / "reverse_report.md").read_text(encoding="utf-8")
            spec = (folder / "reverse" / "reversed_experiment_spec.yaml").read_text(encoding="utf-8")
            self.assertIn("Detected PsychoPy-like Python code", report)
            self.assertIn("TODO", spec)
            self.assertIn("space", spec)

    def test_reverse_handwritten_psychtoolbox(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "handwritten"
            folder.mkdir()
            code = folder / "psychtoolbox_task.m"
            shutil.copy(ROOT / "tests" / "fixtures" / "handwritten" / "psychtoolbox_task.m", code)
            run([sys.executable, "scripts/reverse_engineer.py", str(code)])

            report = (folder / "reverse" / "reverse_report.md").read_text(encoding="utf-8")
            spec = (folder / "reverse" / "reversed_experiment_spec.yaml").read_text(encoding="utf-8")
            self.assertIn("Screen('Flip')", report)
            self.assertIn("KbCheck", report)
            self.assertIn("TODO", spec)


if __name__ == "__main__":
    unittest.main()
