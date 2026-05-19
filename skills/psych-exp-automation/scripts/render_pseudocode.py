#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_dir, read_spec


def render(spec: dict) -> str:
    meta = spec["metadata"]
    runtime = spec.get("runtime", {})
    lines: list[str] = []
    lines.append(f"# {meta['title']} - 结构化伪代码")
    lines.append("")
    lines.append("## 1. 实验概览 / Overview")
    lines.append(f"- 实验 ID / Experiment ID: `{meta['experiment_id']}`")
    lines.append(f"- 实验名称 / Title: `{meta['title']}`")
    lines.append(f"- 研究目的 / Purpose: {meta.get('purpose', '')}")
    lines.append(f"- 参考范式 / Reference: `{meta.get('paradigm_reference', 'none')}`（仅作参考，不限制流程）")
    lines.append(f"- 实验呈现语言 / Runtime language: `{runtime.get('language', 'not specified')}`")
    lines.append(f"- 默认平台 / Default platform: `{spec['target_platform']['default']}`")
    timing = spec.get("timing", {})
    lines.append(f"- 时间控制 / Timing control: `{timing.get('control', 'frame')}`（所有定时事件按屏幕刷新帧控制）")
    lines.append("")
    lines.append("## 2. 全局参数与设计 / Global Design")
    lines.append(f"- 设计类型 / Design type: `{spec['design']['design_type']}`")
    lines.append("- 自变量 / Independent variables:")
    for iv in spec["design"].get("independent_variables", []):
        lines.append(f"  - `{iv.get('id', iv.get('name'))}`: {iv.get('name', '')}, levels={iv.get('levels')}")
    lines.append("- 因变量 / Dependent variables:")
    for dv in spec["design"].get("dependent_variables", []):
        lines.append(f"  - `{dv.get('id', dv.get('name'))}`: {dv.get('name', '')}, unit={dv.get('unit', '')}")
    lines.append(f"- 随机化 / Randomization: {spec['design'].get('randomization', 'not specified')}")
    lines.append(f"- 平衡策略 / Counterbalancing: {spec['design'].get('counterbalancing', 'not specified')}")
    lines.append("")
    lines.append("## 3. 实验流程定义 / Procedure")
    lines.append("### 3.1 Block 序列 / Block Sequence")
    for block in spec["blocks"]:
        trials = block["trials"]
        lines.append(
            f"- `{block['id']}` ({block.get('type', '')}): source=`{trials['source']}`, "
            f"order=`{trials['order']}`, repetitions=`{trials['repetitions']}`, feedback=`{block.get('feedback', False)}`"
        )
        if block.get("instruction"):
            lines.append(f"  - 指导语 / Instruction: {block['instruction']}")
    lines.append("")
    lines.append("### 3.2 Trial 微观结构 / Trial Events")
    for index, ev in enumerate(spec["trial_structure"]["events"], start=1):
        lines.append(f"{index}. Event `{ev['id']}`: type=`{ev['type']}`")
        if "content" in ev:
            lines.append(f"   - content: `{ev['content']}`")
        if "color" in ev:
            lines.append(f"   - color: `{ev['color']}`")
        if "duration_ms" in ev:
            lines.append(f"   - duration_ms: `{ev['duration_ms']}`")
        if "max_duration_ms" in ev:
            lines.append(f"   - max_duration_ms: `{ev['max_duration_ms']}`")
        if "choices" in ev:
            lines.append(f"   - choices: `{ev['choices']}`")
        if "correct_key" in ev:
            lines.append(f"   - correct_key: `{ev['correct_key']}`")
        if "show_when" in ev:
            lines.append(f"   - show_when: `{ev['show_when']}`")
    lines.append("")
    lines.append("## 4. 数据记录规范 / Data Logging")
    for field in spec["data"]["fields"]:
        lines.append(f"- `{field}`")
    lines.append("")
    lines.append("## 5. 文件与输出设置 / Output")
    output = spec["output"]
    lines.append(f"- format: `{output['format']}`")
    lines.append(f"- directory: `{output['directory']}`")
    lines.append(f"- filename_template: `{output['filename_template']}`")
    lines.append("")
    lines.append("[End of Pseudocode]")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    spec = read_spec(args.spec)
    text = render(spec)
    if args.out:
        ensure_dir(args.out.parent)
        args.out.write_text(text, encoding="utf-8")
        print(args.out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
