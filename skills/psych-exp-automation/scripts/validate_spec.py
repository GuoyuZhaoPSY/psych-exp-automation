#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from common import read_spec


REQUIRED_TOP = ["version", "metadata", "runtime", "target_platform", "design", "timing", "trial_structure", "blocks", "data", "output"]
EVENT_TYPES = {"instruction", "text", "keyboard_response", "feedback", "blank"}
PLATFORMS = {"psychopy", "psychtoolbox"}


def validate(spec: dict) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP:
        if key not in spec:
            errors.append(f"Missing top-level key: {key}")

    metadata = spec.get("metadata", {})
    for key in ["experiment_id", "title"]:
        if not metadata.get(key):
            errors.append(f"metadata.{key} is required")

    runtime = spec.get("runtime", {})
    if not runtime.get("language"):
        errors.append("runtime.language is required")

    target = spec.get("target_platform", {})
    if target.get("default") not in PLATFORMS:
        errors.append("target_platform.default must be psychopy or psychtoolbox")
    for platform in target.get("supported", []):
        if platform not in PLATFORMS:
            errors.append(f"Unsupported platform listed: {platform}")

    timing = spec.get("timing", {})
    if timing.get("control", "frame") != "frame":
        errors.append("timing.control must be 'frame' so event durations are controlled per screen refresh frame")
    if float(timing.get("frame_rate_fallback_hz", 60)) <= 0:
        errors.append("timing.frame_rate_fallback_hz must be positive")

    design = spec.get("design", {})
    if not design.get("independent_variables"):
        warnings.append("design.independent_variables is empty; okay for some tasks, but confirm this is intentional")
    if not design.get("dependent_variables"):
        errors.append("design.dependent_variables must include at least one DV")

    conditions = spec.get("conditions", [])
    if not isinstance(conditions, list) or not conditions:
        errors.append("conditions must contain at least one trial row in v0.1")

    response_events = 0
    for index, ev in enumerate(spec.get("trial_structure", {}).get("events", []), start=1):
        ev_id = ev.get("id", f"event_{index}")
        if ev.get("type") not in EVENT_TYPES:
            errors.append(f"trial_structure.events[{index}] has unknown type: {ev.get('type')}")
        if ev.get("type") == "keyboard_response":
            response_events += 1
            if not ev.get("choices"):
                errors.append(f"keyboard_response event {ev_id} needs choices")
            if not ev.get("correct_key"):
                warnings.append(f"keyboard_response event {ev_id} has no correct_key; accuracy cannot be computed")
            if not ev.get("max_duration_ms"):
                errors.append(f"keyboard_response event {ev_id} needs max_duration_ms")
        if ev.get("type") in {"text", "blank", "feedback"} and "duration_ms" not in ev:
            errors.append(f"event {ev_id} needs duration_ms")

    if response_events == 0:
        warnings.append("No keyboard_response event found; this may be a passive-viewing experiment")

    block_ids = set()
    for block in spec.get("blocks", []):
        block_id = block.get("id")
        if not block_id:
            errors.append("Each block needs an id")
        if block_id in block_ids:
            errors.append(f"Duplicate block id: {block_id}")
        block_ids.add(block_id)
        trials = block.get("trials", {})
        if trials.get("source") != "conditions":
            errors.append(f"Block {block_id} uses unsupported trials.source {trials.get('source')!r} in v0.1")
        if trials.get("order") not in {"fixed", "random"}:
            errors.append(f"Block {block_id} trials.order must be fixed or random")
        if int(trials.get("repetitions", 0)) < 1:
            errors.append(f"Block {block_id} trials.repetitions must be >= 1")

    fields = spec.get("data", {}).get("fields", [])
    for field in ["participant_id", "block_id", "response", "rt", "correct"]:
        if field not in fields:
            warnings.append(f"data.fields does not include common field: {field}")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    spec = read_spec(args.spec)
    errors, warnings = validate(spec)

    print(f"Spec: {args.spec}")
    if errors:
        print("Status: FAIL")
        for item in errors:
            print(f"ERROR: {item}")
    else:
        print("Status: PASS")
    for item in warnings:
        print(f"WARNING: {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
