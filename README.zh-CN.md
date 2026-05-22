# 心理学实验自动化工作流

[English](README.md) | 中文

心理学实验自动化工作流帮助研究者把实验设计转化为一套可复现、可检查、可协作的编程流程：

1. 撰写或澄清实验设计
2. 编码为 `ExperimentSpec` YAML
3. 生成可审阅的 Markdown 伪代码
4. 生成 PsychoPy 或 Psychtoolbox 代码
5. 根据规格验证生成代码

这个项目的目标是降低心理学、认知科学、认知神经科学研究者的 coding 门槛，同时不把实验限制在固定的经典范式列表里。Stroop、Flanker、Go/No-Go、N-back 等名称可以作为参考标签，但系统真正使用的是通用的 `block -> trial -> event` 结构。

本项目也支持逆向工作流：已有 PsychoPy 或 Psychtoolbox 代码可以被转换回 YAML 草案和自然语言实验说明。这适合用于理解、迁移或重构旧实验脚本。

## Codex 生成说明

本仓库由 Codex 辅助搭建并迭代生成。生成内容包括工作流脚本、可安装的 Codex Skill、demo 实验和验证产物。研究者仍然需要进行人工审查：生成的实验代码在正式采集数据前必须经过代码检查、pilot test 和目标机器上的时序验证。

## 这个项目在做什么

这个项目不是要求研究者直接从零编写 PsychoPy 或 Psychtoolbox 代码，而是让研究者先用结构化 YAML 描述实验。YAML 作为实验设计和可执行代码之间的桥梁。

它的好处包括：

- 让实验逻辑更容易阅读和讨论
- 把设计、伪代码、生成代码和验证报告放在同一个实验文件夹
- 减少重复样板代码
- 支持中文、英文或其他自然语言实验文本
- 保留一份机器可检查的唯一真源
- 鼓励视觉事件使用 frame-level timing control
- 帮助从已有 PsychoPy/Psychtoolbox 代码恢复实验文档

## 核心原则

- `experiment_spec.yaml` 是唯一真源。
- 每个实验一个独立文件夹。
- 实验文本可以直接使用中文、英文或其他自然语言。
- 定时事件使用 frame-level timing control。
- 第一版支持 PsychoPy 和 Psychtoolbox。
- 生成代码必须在正式采集数据前人工检查、试运行和 pilot test。

## 最小 YAML 示例

下面是一个简化版 `ExperimentSpec`。完整 Stroop 示例见 [demo/stroop/experiment_spec.yaml](demo/stroop/experiment_spec.yaml)。

```yaml
version: "0.1.0"

metadata:
  experiment_id: "simple_reaction_time"
  title: "简单反应时任务"
  purpose: "测量被试对视觉目标的反应速度。"

runtime:
  language: "zh-CN"
  continue_key: "space"
  welcome_text: "目标出现后请尽快按键。"
  end_text: "实验结束，感谢参与。"
  continue_text: "按空格键继续"

target_platform:
  default: "psychopy"
  supported: ["psychopy", "psychtoolbox"]

timing:
  control: "frame"
  frame_rate_fallback_hz: 60
  duration_rounding: "nearest_frame"

conditions:
  - stimulus: "X"
    correct_key: "space"

trial_structure:
  events:
    - id: "fixation"
      type: "text"
      content: "+"
      duration_ms: 500
    - id: "target"
      type: "keyboard_response"
      content: "$trial.stimulus"
      choices: ["space"]
      correct_key: "$trial.correct_key"
      max_duration_ms: 1500
      record_response: true
    - id: "iti"
      type: "blank"
      duration_ms:
        random_uniform: [500, 1000]

blocks:
  - id: "main"
    type: "formal"
    instruction: "请尽快且准确地反应。"
    feedback: false
    trials:
      source: "conditions"
      order: "random"
      repetitions: 20

data:
  fields: ["participant_id", "block_id", "event_id", "response", "rt", "correct", "timestamp"]

output:
  format: "csv"
  directory: "data"
  filename_template: "{experiment_id}_{participant_id}_{date}.csv"
```

## 仓库结构

```text
psych-exp-automation/
  demo/stroop/
    experiment_spec.yaml
    pseudocode.md
    psychopy/
    psychtoolbox/

  scripts/
    run_pipeline.py
    validate_spec.py
    render_pseudocode.py
    generate_code.py
    validate_generated_code.py

  schemas/
    experiment_spec.schema.json

  skills/psych-exp-automation/
    SKILL.md
    scripts/
    schemas/
    references/

  tests/
    fixtures/stroop/
    test_pipeline.py
```

研究者自己的实验建议单独建文件夹：

```text
my_experiment/
  experiment_spec.yaml
  pseudocode.md
  psychopy/
  psychtoolbox/
```

## 快速开始

运行 Stroop demo：

```bash
python3 scripts/run_pipeline.py demo/stroop/experiment_spec.yaml --platform psychopy
python3 scripts/run_pipeline.py demo/stroop/experiment_spec.yaml --platform psychtoolbox
```

运行后会生成或更新：

```text
demo/stroop/pseudocode.md
demo/stroop/psychopy/run_experiment.py
demo/stroop/psychopy/validation_report.md
demo/stroop/psychtoolbox/stroop_color_word.m
demo/stroop/psychtoolbox/validation_report.md
```

## 逆向工程

逆向工程会把已有代码转换为：

```text
reverse/
  reversed_experiment_spec.yaml
  design_description.md
  reverse_report.md
  llm_prompt.md
```

运行示例：

```bash
python3 scripts/reverse_engineer.py demo/stroop/psychopy/run_experiment.py
```

逆向优先级：

1. 如果存在 `experiment_spec.snapshot.json`，直接从 snapshot 还原
2. 如果是本项目生成的 PsychoPy/Psychtoolbox 代码，读取内嵌常量
3. 如果是手写 PsychoPy/Psychtoolbox 代码，使用 best-effort 启发式解析

对于手写代码，生成的 YAML 是草案。无法确定或存在歧义的信息会保留为 `TODO`，并写入 `reverse_report.md`。逆向工作流适合理解和迁移旧代码，但不能保证完整恢复原始研究意图。

## 作为 Codex Skill 安装

发布到 GitHub 后，可以让 Codex 安装：

```text
Use skill-installer to install the skill from GuoyuZhaoPSY/psych-exp-automation at skills/psych-exp-automation.
```

也可以手动安装：

```bash
mkdir -p ~/.codex/skills
cp -R skills/psych-exp-automation ~/.codex/skills/
```

安装后重启 Codex。

## ExperimentSpec

`ExperimentSpec` 是 YAML 中间表示。英文键用于机器解析，字段值和注释可以使用实验本身的自然语言。

主要部分：

- `metadata`：实验 ID、标题、目的
- `runtime`：呈现给被试的语言和文本
- `target_platform`：`psychopy` 或 `psychtoolbox`
- `design`：变量、水平、随机化、平衡策略
- `timing`：frame-level timing 设置
- `conditions`：trial 级条件行
- `trial_structure`：每个 trial 内的 event 序列
- `blocks`：block 顺序、重复次数、反馈
- `data`：输出字段
- `output`：CSV 文件名和路径

## 测试

```bash
python3 -m unittest discover -s tests
```

测试会把 Stroop fixture 分别跑过 PsychoPy 和 Psychtoolbox 代码生成器，并验证生成结果。测试不会启动 PsychoPy 或 MATLAB。

## 科学使用注意事项

这个项目可以加速编程，但不能替代实验验证。正式采集数据前，请务必：

- 检查生成代码
- 运行 pilot
- 在目标机器上验证时序
- 检查数据输出
- 对 EEG、fMRI、眼动或其他外部设备确认 trigger 和同步逻辑

## 贡献

欢迎贡献：

- 新 event 类型，例如 image、audio、video、mouse response、slider、rating scale、scanner trigger
- 更强的验证规则
- 更好的 PsychoPy 或 Psychtoolbox 后端
- 真实实验设计案例
- 教学文档

请参考 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

本项目使用 [MIT License](LICENSE)。
