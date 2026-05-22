#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import dump_yaml, ensure_dir


PLATFORM_DIRS = {"psychopy", "psychtoolbox"}
TODO = "TODO: reverse engineering could not determine this value."


@dataclass
class ReverseResult:
    spec: dict[str, Any]
    platform: str
    confidence: str
    parsed: list[str]
    inferred: list[str]
    todos: list[str]
    evidence: list[str]
    source: Path


def strip_internal_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: strip_internal_keys(v) for k, v in value.items() if not str(k).startswith("_")}
    if isinstance(value, list):
        return [strip_internal_keys(v) for v in value]
    return value


def infer_experiment_dir(path: Path) -> Path:
    if path.is_file():
        return path.parent.parent if path.parent.name in PLATFORM_DIRS else path.parent
    if path.name in PLATFORM_DIRS:
        return path.parent
    return path


def find_snapshot(path: Path) -> Path | None:
    candidates: list[Path] = []
    if path.is_file():
        candidates.extend([path.parent / "experiment_spec.snapshot.json", path.parent.parent / "experiment_spec.snapshot.json"])
    else:
        candidates.extend(
            [
                path / "experiment_spec.snapshot.json",
                path / "psychopy" / "experiment_spec.snapshot.json",
                path / "psychtoolbox" / "experiment_spec.snapshot.json",
            ]
        )
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def detect_code_file(path: Path, platform: str) -> tuple[Path, str]:
    if path.is_file():
        detected = detect_platform(path, platform)
        return path, detected
    files = list(path.glob("*.py")) + list(path.glob("*.m")) + list(path.glob("psychopy/*.py")) + list(path.glob("psychtoolbox/*.m"))
    for file in files:
        detected = detect_platform(file, platform)
        if platform != "auto" or detected != "unknown":
            return file, detected
    raise FileNotFoundError(f"No PsychoPy or Psychtoolbox code file found under {path}")


def detect_platform(path: Path, platform: str) -> str:
    if platform != "auto":
        return platform
    suffix = path.suffix.lower()
    text = path.read_text(encoding="utf-8", errors="replace")[:20000]
    if suffix == ".py" or "psychopy" in text.lower() or "visual.Window" in text:
        return "psychopy"
    if suffix == ".m" or "PsychDefaultSetup" in text or "Screen('Flip'" in text or "KbCheck" in text:
        return "psychtoolbox"
    return "unknown"


def default_spec(platform: str) -> dict[str, Any]:
    return {
        "version": "0.1.0",
        "metadata": {
            "experiment_id": "reversed_experiment",
            "title": "TODO: recovered experiment title",
            "purpose": "TODO: describe the original research purpose.",
            "paradigm_reference": "TODO: infer only if clearly stated in code.",
        },
        "runtime": {
            "language": "zh-CN",
            "continue_key": "space",
            "welcome_text": TODO,
            "end_text": TODO,
            "continue_text": "按空格键继续",
        },
        "target_platform": {"default": platform if platform in PLATFORM_DIRS else "psychopy", "supported": ["psychopy", "psychtoolbox"]},
        "participant": {"collection_mode": "runtime_dialog", "fields": [{"id": "participant_id", "label": "被试编号", "required": True}]},
        "design": {
            "design_type": "TODO: infer within_subject / between_subject / mixed if possible.",
            "independent_variables": [],
            "dependent_variables": [{"id": "rt", "name": "反应时", "unit": "ms"}, {"id": "correct", "name": "正确性", "unit": "boolean"}],
            "randomization": "TODO: determine trial/block randomization from source code.",
            "counterbalancing": "TODO: determine counterbalancing from source code.",
        },
        "display": {"background_color": [0, 0, 0], "text_color": [1, 1, 1], "font_size": 48, "screen_mode": "TODO: windowed/fullscreen"},
        "timing": {"control": "frame", "frame_rate_fallback_hz": 60, "duration_rounding": "nearest_frame"},
        "conditions": [],
        "trial_structure": {"events": []},
        "blocks": [
            {
                "id": "main",
                "type": "formal",
                "instruction": TODO,
                "feedback": False,
                "trials": {"source": "conditions", "order": "TODO: fixed/random", "repetitions": 1},
            }
        ],
        "data": {"fields": ["participant_id", "block_id", "event_id", "response", "rt", "correct", "timestamp"]},
        "output": {"format": "csv", "directory": "data", "filename_template": "{experiment_id}_{participant_id}_{date}.csv"},
    }


def from_snapshot(snapshot: Path) -> ReverseResult:
    spec = strip_internal_keys(json.loads(snapshot.read_text(encoding="utf-8")))
    platform = spec.get("target_platform", {}).get("default", "unknown")
    return ReverseResult(
        spec=spec,
        platform=platform,
        confidence="high",
        parsed=["Loaded experiment_spec.snapshot.json"],
        inferred=[],
        todos=[],
        evidence=[f"Snapshot: {snapshot}"],
        source=snapshot,
    )


def python_constants(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    constants: dict[str, Any] = {}
    wanted = {"EXPERIMENT_ID", "TITLE", "RUNTIME", "TIMING", "CONDITIONS", "BLOCKS", "TRIAL_EVENTS", "DATA_FIELDS", "OUTPUT_DIRECTORY", "FILENAME_TEMPLATE"}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in wanted:
                    try:
                        constants[target.id] = ast.literal_eval(node.value)
                    except Exception:
                        pass
    return constants


def from_generated_psychopy(path: Path) -> ReverseResult | None:
    constants = python_constants(path)
    if not {"EXPERIMENT_ID", "TITLE", "TRIAL_EVENTS", "BLOCKS"}.issubset(constants):
        return None
    spec = default_spec("psychopy")
    spec["metadata"]["experiment_id"] = constants.get("EXPERIMENT_ID", "reversed_experiment")
    spec["metadata"]["title"] = constants.get("TITLE", "TODO: recovered experiment title")
    spec["runtime"].update(constants.get("RUNTIME", {}))
    spec["timing"].update(constants.get("TIMING", {}))
    spec["conditions"] = constants.get("CONDITIONS", [])
    spec["trial_structure"]["events"] = constants.get("TRIAL_EVENTS", [])
    spec["blocks"] = constants.get("BLOCKS", spec["blocks"])
    spec["data"]["fields"] = constants.get("DATA_FIELDS", spec["data"]["fields"])
    spec["output"]["directory"] = constants.get("OUTPUT_DIRECTORY", "data")
    spec["output"]["filename_template"] = constants.get("FILENAME_TEMPLATE", "{experiment_id}_{participant_id}_{date}.csv")
    return ReverseResult(
        spec=spec,
        platform="psychopy",
        confidence="medium-high",
        parsed=["Recovered generated PsychoPy constants", "Recovered trial event sequence and block definitions"],
        inferred=["Design variables and purpose remain TODO unless present in embedded constants"],
        todos=["Confirm design variables, research purpose, and counterbalancing."],
        evidence=[f"Parsed constants from {path}"],
        source=path,
    )


class MatlabLiteralParser:
    def __init__(self, text: str):
        self.text = text
        self.i = 0

    def parse(self) -> Any:
        value = self.value()
        self.ws()
        return value

    def ws(self) -> None:
        while self.i < len(self.text) and self.text[self.i].isspace():
            self.i += 1

    def peek(self, s: str) -> bool:
        return self.text.startswith(s, self.i)

    def value(self) -> Any:
        self.ws()
        if self.peek("struct("):
            return self.struct()
        if self.i < len(self.text) and self.text[self.i] == "'":
            return self.string()
        if self.i < len(self.text) and self.text[self.i] == "{":
            return self.cell()
        if self.i < len(self.text) and self.text[self.i] == "[":
            return self.array()
        if self.peek("true"):
            self.i += 4
            return True
        if self.peek("false"):
            self.i += 5
            return False
        return self.number_or_symbol()

    def string(self) -> str:
        self.i += 1
        out = []
        while self.i < len(self.text):
            ch = self.text[self.i]
            if ch == "'":
                if self.i + 1 < len(self.text) and self.text[self.i + 1] == "'":
                    out.append("'")
                    self.i += 2
                    continue
                self.i += 1
                return "".join(out)
            out.append(ch)
            self.i += 1
        return "".join(out)

    def cell(self) -> list[Any]:
        self.i += 1
        items = []
        while self.i < len(self.text):
            self.ws()
            if self.i < len(self.text) and self.text[self.i] == "}":
                self.i += 1
                return items
            items.append(self.value())
            self.ws()
            if self.i < len(self.text) and self.text[self.i] == ",":
                self.i += 1
        return items

    def array(self) -> list[Any]:
        end = self.text.find("]", self.i)
        raw = self.text[self.i + 1 : end if end != -1 else len(self.text)]
        self.i = len(self.text) if end == -1 else end + 1
        values = []
        for part in re.split(r"[\s,]+", raw.strip()):
            if part:
                values.append(float(part) if "." in part else int(part))
        return values

    def struct(self) -> dict[str, Any]:
        self.i += len("struct(")
        obj = {}
        while self.i < len(self.text):
            self.ws()
            if self.i < len(self.text) and self.text[self.i] == ")":
                self.i += 1
                return obj
            key = self.value()
            self.ws()
            if self.i < len(self.text) and self.text[self.i] == ",":
                self.i += 1
            val = self.value()
            obj[str(key)] = val
            self.ws()
            if self.i < len(self.text) and self.text[self.i] == ",":
                self.i += 1
        return obj

    def number_or_symbol(self) -> Any:
        start = self.i
        while self.i < len(self.text) and self.text[self.i] not in ",)}":
            self.i += 1
        raw = self.text[start : self.i].strip()
        try:
            return float(raw) if "." in raw else int(raw)
        except ValueError:
            return raw


def matlab_assignment(text: str, name: str) -> Any:
    match = re.search(rf"^\s*{re.escape(name)}\s*=\s*(.+?);", text, re.MULTILINE | re.DOTALL)
    if not match:
        return None
    return MatlabLiteralParser(match.group(1).strip()).parse()


def from_generated_psychtoolbox(path: Path) -> ReverseResult | None:
    text = path.read_text(encoding="utf-8", errors="replace")
    experiment_id = matlab_assignment(text, "experimentId")
    title = matlab_assignment(text, "titleText")
    trial_events = matlab_assignment(text, "trialEvents")
    blocks = matlab_assignment(text, "blocks")
    if not experiment_id or not title or not trial_events or not blocks:
        return None
    spec = default_spec("psychtoolbox")
    spec["metadata"]["experiment_id"] = experiment_id
    spec["metadata"]["title"] = title
    spec["runtime"].update(matlab_assignment(text, "runtime") or {})
    spec["timing"].update(matlab_assignment(text, "timing") or {})
    spec["conditions"] = matlab_assignment(text, "conditions") or []
    spec["trial_structure"]["events"] = trial_events
    spec["blocks"] = blocks
    spec["data"]["fields"] = matlab_assignment(text, "dataFields") or spec["data"]["fields"]
    spec["output"]["directory"] = matlab_assignment(text, "outputDirectory") or "data"
    spec["output"]["filename_template"] = matlab_assignment(text, "filenameTemplate") or "{experiment_id}_{participant_id}_{date}.csv"
    return ReverseResult(
        spec=spec,
        platform="psychtoolbox",
        confidence="medium-high",
        parsed=["Recovered generated Psychtoolbox variables", "Recovered trial event sequence and block definitions"],
        inferred=["Design variables and purpose remain TODO unless present in embedded variables"],
        todos=["Confirm design variables, research purpose, and counterbalancing."],
        evidence=[f"Parsed generated MATLAB assignments from {path}"],
        source=path,
    )


def quoted_strings(text: str) -> list[str]:
    items = re.findall(r"['\"]([^'\"]{1,120})['\"]", text)
    return [s for s in items if not s.startswith("$") and s not in {"", "NO_KEYS"}]


def hand_written_psychopy(path: Path) -> ReverseResult:
    text = path.read_text(encoding="utf-8", errors="replace")
    spec = default_spec("psychopy")
    spec["metadata"]["experiment_id"] = path.stem
    spec["metadata"]["title"] = f"TODO: reversed from {path.name}"
    strings = quoted_strings(text)
    keys = sorted(set(re.findall(r"keyList\s*=\s*\[([^\]]+)\]|choices\s*=\s*\[([^\]]+)\]", text)))
    flat_keys = sorted(set(re.findall(r"['\"]([a-zA-Z0-9_ -]+)['\"]", " ".join(" ".join(k) for k in keys))))
    durations = [int(float(x) * 1000) for x in re.findall(r"core\.wait\((\d+(?:\.\d+)?)\)", text)]
    durations.extend(int(x) for x in re.findall(r"duration_ms\s*=\s*(\d+)|trial_duration\s*[:=]\s*(\d+)", text) for x in x if x)
    content = next((s for s in strings if len(s) <= 20 and s not in flat_keys), "TODO: identify stimulus content")
    spec["conditions"] = [{"stimulus": content, "correct_key": flat_keys[0] if flat_keys else "TODO: identify correct key"}]
    spec["trial_structure"]["events"] = [
        {"id": "stimulus", "type": "keyboard_response", "content": "$trial.stimulus", "choices": flat_keys or ["TODO: identify response keys"], "correct_key": "$trial.correct_key", "max_duration_ms": max(durations) if durations else "TODO: identify response window", "record_response": True}
    ]
    if durations:
        spec["trial_structure"]["events"].insert(0, {"id": "timed_event", "type": "text", "content": content, "duration_ms": durations[0]})
    instruction = next((s for s in strings if len(s) > 20), TODO)
    spec["blocks"][0]["instruction"] = instruction
    parsed = ["Detected PsychoPy-like Python code"]
    inferred = []
    todos = ["Confirm experiment design, conditions, block structure, output filename, and whether extracted strings are stimuli or instructions."]
    if "csv" in text or "DictWriter" in text:
        parsed.append("Detected CSV/data writing code")
    else:
        todos.append("Could not identify data output code.")
    evidence = [f"Source: {path}", f"Detected keys: {flat_keys or 'none'}", f"Detected durations_ms: {durations or 'none'}"]
    return ReverseResult(spec, "psychopy", "low", parsed, inferred, todos, evidence, path)


def hand_written_psychtoolbox(path: Path) -> ReverseResult:
    text = path.read_text(encoding="utf-8", errors="replace")
    spec = default_spec("psychtoolbox")
    spec["metadata"]["experiment_id"] = path.stem
    spec["metadata"]["title"] = f"TODO: reversed from {path.name}"
    strings = quoted_strings(text)
    keys = sorted(set(re.findall(r"KbName\(['\"]([^'\"]+)['\"]\)|strcmp\([^,]+,\s*['\"]([^'\"]+)['\"]\)", text)))
    flat_keys = sorted(set(k for pair in keys for k in pair if k))
    waits = [int(float(x) * 1000) for x in re.findall(r"WaitSecs\((\d+(?:\.\d+)?)\)", text)]
    stimulus = next((s for s in strings if len(s) <= 20 and s not in flat_keys), "TODO: identify stimulus content")
    spec["conditions"] = [{"stimulus": stimulus, "correct_key": flat_keys[0] if flat_keys else "TODO: identify correct key"}]
    spec["trial_structure"]["events"] = [
        {"id": "stimulus", "type": "keyboard_response", "content": "$trial.stimulus", "choices": flat_keys or ["TODO: identify response keys"], "correct_key": "$trial.correct_key", "max_duration_ms": max(waits) if waits else "TODO: identify response window", "record_response": True}
    ]
    if waits:
        spec["trial_structure"]["events"].insert(0, {"id": "timed_event", "type": "text", "content": stimulus, "duration_ms": waits[0]})
    spec["blocks"][0]["instruction"] = next((s for s in strings if len(s) > 20), TODO)
    parsed = ["Detected Psychtoolbox-like MATLAB code"]
    if "Screen('Flip'" in text or 'Screen("Flip"' in text:
        parsed.append("Detected Screen('Flip') calls")
    if "KbCheck" in text:
        parsed.append("Detected KbCheck response polling")
    todos = ["Confirm experiment design, conditions, block structure, output filename, and timing semantics."]
    evidence = [f"Source: {path}", f"Detected keys: {flat_keys or 'none'}", f"Detected waits_ms: {waits or 'none'}"]
    return ReverseResult(spec, "psychtoolbox", "low", parsed, [], todos, evidence, path)


def reverse_code(path: Path, platform: str) -> ReverseResult:
    snapshot = find_snapshot(path)
    if snapshot:
        return from_snapshot(snapshot)
    code_file, detected = detect_code_file(path, platform)
    if detected == "psychopy":
        return from_generated_psychopy(code_file) or hand_written_psychopy(code_file)
    if detected == "psychtoolbox":
        return from_generated_psychtoolbox(code_file) or hand_written_psychtoolbox(code_file)
    raise ValueError(f"Could not detect supported platform for {path}")


def description_language(spec: dict[str, Any]) -> str:
    return "zh" if str(spec.get("runtime", {}).get("language", "zh-CN")).lower().startswith("zh") else "en"


def render_description(result: ReverseResult) -> str:
    spec = result.spec
    zh = description_language(spec) == "zh"
    meta = spec.get("metadata", {})
    events = spec.get("trial_structure", {}).get("events", [])
    blocks = spec.get("blocks", [])
    fields = spec.get("data", {}).get("fields", [])
    lines: list[str] = []
    if zh:
        lines.extend(
            [
                f"# {meta.get('title', '逆向实验说明')}",
                "",
                "## 概览",
                f"- 实验 ID：`{meta.get('experiment_id', 'TODO')}`",
                f"- 研究目的：{meta.get('purpose', TODO)}",
                f"- 目标平台：`{spec.get('target_platform', {}).get('default', result.platform)}`",
                f"- 逆向置信度：`{result.confidence}`",
                "",
                "## 实验流程",
            ]
        )
        for block in blocks:
            lines.append(f"- Block `{block.get('id')}`：{block.get('instruction', TODO)}")
        lines.extend(["", "## Trial 结构"])
        for ev in events:
            lines.append(f"- `{ev.get('id')}` ({ev.get('type')}): content={ev.get('content', '')}, duration={ev.get('duration_ms', ev.get('max_duration_ms', ''))}")
        lines.extend(["", "## 数据记录", *[f"- `{field}`" for field in fields], "", "## TODO"])
        lines.extend([f"- {todo}" for todo in (result.todos or ["无明确 TODO。"])])
    else:
        lines.extend(
            [
                f"# {meta.get('title', 'Reversed Experiment Description')}",
                "",
                "## Overview",
                f"- Experiment ID: `{meta.get('experiment_id', 'TODO')}`",
                f"- Purpose: {meta.get('purpose', TODO)}",
                f"- Target platform: `{spec.get('target_platform', {}).get('default', result.platform)}`",
                f"- Reverse confidence: `{result.confidence}`",
                "",
                "## Procedure",
            ]
        )
        for block in blocks:
            lines.append(f"- Block `{block.get('id')}`: {block.get('instruction', TODO)}")
        lines.extend(["", "## Trial Structure"])
        for ev in events:
            lines.append(f"- `{ev.get('id')}` ({ev.get('type')}): content={ev.get('content', '')}, duration={ev.get('duration_ms', ev.get('max_duration_ms', ''))}")
        lines.extend(["", "## Data Logging", *[f"- `{field}`" for field in fields], "", "## TODO"])
        lines.extend([f"- {todo}" for todo in (result.todos or ["No explicit TODO items."])])
    return "\n".join(lines) + "\n"


def render_report(result: ReverseResult) -> str:
    lines = [
        "# Reverse Engineering Report",
        "",
        f"- Source: `{result.source}`",
        f"- Platform: `{result.platform}`",
        f"- Confidence: `{result.confidence}`",
        "",
        "## Parsed Items",
        *[f"- {item}" for item in result.parsed],
        "",
        "## Inferred Items",
        *[f"- {item}" for item in (result.inferred or ["None"])],
        "",
        "## TODO / Unresolved",
        *[f"- {item}" for item in (result.todos or ["None"])],
        "",
        "## Evidence",
        *[f"- {item}" for item in result.evidence],
    ]
    return "\n".join(lines) + "\n"


def render_llm_prompt(result: ReverseResult) -> str:
    return (
        "# LLM Assistance Prompt\n\n"
        "Use the source code, reversed_experiment_spec.yaml, and reverse_report.md to improve the ExperimentSpec. "
        "Only fill fields supported by evidence in the source code. Keep TODO values when evidence is missing. "
        "Do not invent experimental design intent.\n\n"
        f"Source: {result.source}\n"
        f"Platform: {result.platform}\n"
        f"Confidence: {result.confidence}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("code_or_folder", type=Path)
    parser.add_argument("--platform", choices=["auto", "psychopy", "psychtoolbox"], default="auto")
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    source = args.code_or_folder.resolve()
    result = reverse_code(source, args.platform)
    out_dir = ensure_dir(args.out or infer_experiment_dir(source) / "reverse")
    dump_yaml(result.spec, out_dir / "reversed_experiment_spec.yaml")
    (out_dir / "design_description.md").write_text(render_description(result), encoding="utf-8")
    (out_dir / "reverse_report.md").write_text(render_report(result), encoding="utf-8")
    (out_dir / "llm_prompt.md").write_text(render_llm_prompt(result), encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
