from __future__ import annotations

import json
import random
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load YAML through Ruby's stdlib Psych so this project has no Python YAML dependency."""
    path = Path(path)
    ruby = (
        "require 'yaml'; require 'json'; "
        "obj = YAML.safe_load(File.read(ARGV[0]), aliases: true); "
        "puts JSON.generate(obj)"
    )
    result = subprocess.run(
        ["ruby", "-e", ruby, str(path)],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def dump_json(data: Any, path: str | Path) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def dump_yaml(data: Any, path: str | Path) -> None:
    """Write YAML through Ruby's stdlib Psych so this project has no Python YAML dependency."""
    path = Path(path)
    ruby = (
        "require 'json'; require 'yaml'; "
        "obj = JSON.parse(STDIN.read); "
        "File.write(ARGV[0], YAML.dump(obj))"
    )
    subprocess.run(
        ["ruby", "-e", ruby, str(path)],
        input=json.dumps(data, ensure_ascii=False),
        check=True,
        text=True,
    )


def read_spec(path: str | Path) -> dict[str, Any]:
    spec = load_yaml(path)
    spec["_source_path"] = str(Path(path).resolve())
    return spec


def ensure_dir(path: str | Path) -> Path:
    out = Path(path)
    out.mkdir(parents=True, exist_ok=True)
    return out


def ref_value(expr: Any, trial: dict[str, Any], block: dict[str, Any] | None = None) -> Any:
    if not isinstance(expr, str) or not expr.startswith("$"):
        return expr
    parts = expr[1:].split(".")
    if not parts:
        return expr
    root = {"trial": trial, "block": block or {}}
    value: Any = root.get(parts[0], expr)
    for key in parts[1:]:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return None
    return value


def duration_expression_ms(value: Any, lang: str) -> str:
    if isinstance(value, dict) and "random_uniform" in value:
        low, high = value["random_uniform"]
        if lang == "python":
            return f"random.uniform({low}, {high})"
        if lang == "matlab":
            return f"({low} + ({high} - {low}) * rand)"
    return str(value)


def expand_trials(spec: dict[str, Any], block: dict[str, Any]) -> list[dict[str, Any]]:
    source_name = block["trials"]["source"]
    if source_name != "conditions":
        raise ValueError(f"Only source='conditions' is implemented in v0.1, got {source_name!r}.")
    rows = list(spec.get("conditions", [])) * int(block["trials"].get("repetitions", 1))
    if block["trials"].get("order") == "random":
        random.shuffle(rows)
    return rows


def today_yyyymmdd() -> str:
    return datetime.now().strftime("%Y%m%d")
