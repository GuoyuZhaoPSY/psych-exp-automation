#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import read_spec


def check_contains(text: str, needle: str, label: str, results: list[tuple[bool, str]]) -> None:
    results.append((needle in text, label))


def validate_psychopy(spec: dict, code_path: Path) -> list[tuple[bool, str]]:
    text = code_path.read_text(encoding="utf-8")
    results: list[tuple[bool, str]] = []
    check_contains(text, "from psychopy import core, event, gui, visual", "imports PsychoPy runtime", results)
    check_contains(text, "TRIAL_EVENTS", "embeds trial event sequence", results)
    check_contains(text, "BLOCKS", "embeds block sequence", results)
    check_contains(text, "csv.DictWriter", "writes CSV data", results)
    check_contains(text, "keyboard_response_for_frames", "collects keyboard responses with frame loop", results)
    check_contains(text, "duration_frames", "converts event durations to frame counts", results)
    check_contains(text, "win.flip()", "uses screen flips for timed event presentation", results)
    for ev in spec["trial_structure"]["events"]:
        check_contains(text, ev["id"], f"contains event id {ev['id']}", results)
        if "duration_ms" in ev and not isinstance(ev["duration_ms"], dict):
            check_contains(text, str(ev["duration_ms"]), f"contains duration {ev['id']}={ev['duration_ms']}ms", results)
        if "max_duration_ms" in ev:
            check_contains(text, str(ev["max_duration_ms"]), f"contains response window {ev['id']}={ev['max_duration_ms']}ms", results)
    for field in spec["data"]["fields"]:
        check_contains(text, field, f"contains data field {field}", results)
    return results


def validate_psychtoolbox(spec: dict, code_path: Path) -> list[tuple[bool, str]]:
    text = code_path.read_text(encoding="utf-8")
    results: list[tuple[bool, str]] = []
    check_contains(text, "PsychDefaultSetup", "initializes Psychtoolbox", results)
    check_contains(text, "PsychImaging('OpenWindow'", "opens PTB window", results)
    check_contains(text, "collectResponseFrames", "collects keyboard responses with frame loop", results)
    check_contains(text, "durationFrames", "converts event durations to frame counts", results)
    check_contains(text, "Screen('Flip'", "uses screen flips for timed event presentation", results)
    check_contains(text, "Screen('Preference', 'SkipSyncTests', 0)", "keeps Psychtoolbox sync tests enabled", results)
    check_contains(text, "writeRows", "writes CSV data", results)
    check_contains(text, "trialEvents", "embeds trial event sequence", results)
    for ev in spec["trial_structure"]["events"]:
        check_contains(text, ev["id"], f"contains event id {ev['id']}", results)
        if "duration_ms" in ev and not isinstance(ev["duration_ms"], dict):
            check_contains(text, str(ev["duration_ms"]), f"contains duration {ev['id']}={ev['duration_ms']}ms", results)
        if "max_duration_ms" in ev:
            check_contains(text, str(ev["max_duration_ms"]), f"contains response window {ev['id']}={ev['max_duration_ms']}ms", results)
    for field in spec["data"]["fields"]:
        check_contains(text, field, f"contains data field {field}", results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("code", type=Path)
    parser.add_argument("--platform", choices=["psychopy", "psychtoolbox"], required=True)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()

    spec = read_spec(args.spec)
    if args.platform == "psychopy":
        results = validate_psychopy(spec, args.code)
    else:
        results = validate_psychtoolbox(spec, args.code)

    passed = sum(1 for ok, _ in results if ok)
    total = len(results)
    lines = [f"# Generated Code Validation", "", f"- Platform: `{args.platform}`", f"- Code: `{args.code}`", f"- Result: `{passed}/{total}` checks passed", ""]
    for ok, label in results:
        mark = "PASS" if ok else "FAIL"
        lines.append(f"- {mark}: {label}")
    text = "\n".join(lines) + "\n"

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
        print(args.report)
    else:
        print(text)

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
