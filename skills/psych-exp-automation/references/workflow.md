# 心理学实验自动化工作流 v0.1

本项目把心理学实验编程拆成一个可验证的流水线：

1. 自然语言实验说明
2. `ExperimentSpec` YAML
3. Markdown 结构化伪代码
4. PsychoPy 或 Psychtoolbox 代码
5. 验证报告

也支持逆向工作流：

1. 读取已有 PsychoPy 或 Psychtoolbox 代码
2. 生成 `reverse/reversed_experiment_spec.yaml`
3. 生成面向研究者阅读的 `reverse/design_description.md`
4. 生成 `reverse/reverse_report.md`，记录已解析内容、推断内容和 TODO

## 设计原则

- 不限定经典范式。Stroop、Flanker、Go/No-Go 等只作为参考标签，不作为能力边界。
- YAML 是唯一真源。Markdown 用于审阅，代码是生成结果。
- 实验由通用的 block、trial、event 组合表达，类似设计一个小型交互程序。
- 平台是可选项：`target_platform.default` 决定默认生成 PsychoPy 还是 Psychtoolbox。
- 英文键用于机器解析；自然语言内容直接写在字段值中，例如 `title`、`purpose`、`instruction`。中文注释用于解释参数含义，不再维护 `name_zh` 这类重复字段。
- 实验运行时呈现语言由 `runtime.language` 指定。
- 编写实验代码时，所有定时事件按 frame 控制：将毫秒时长换算为屏幕刷新帧数，每一帧执行一次 flip，避免长实验或神经影像同步场景中的时间漂移。
- Psychtoolbox 代码默认保留同步测试，不使用 `SkipSyncTests = 1` 作为正式实验代码。
- 逆向手写代码采用 best-effort 策略，不能确认的内容保留为 TODO，不伪造实验设计意图。

## 文件组织

每个实验一个独立文件夹，工作流过程中产生的文件都放在该实验文件夹内。以仓库中的 Stroop demo 为例：

```text
demo/
  stroop/
    experiment_spec.yaml
    pseudocode.md
    psychopy/
      run_experiment.py
      experiment_spec.snapshot.json
      validation_report.md
    psychtoolbox/
      stroop_color_word.m
      experiment_spec.snapshot.json
      validation_report.md
```

研究者自己的新实验可以创建为独立文件夹，例如 `nback/` 或 `my_fmri_task/`。

## 当前支持

- YAML 校验：`scripts/validate_spec.py`
- 伪代码渲染：`scripts/render_pseudocode.py`
- PsychoPy 代码生成：`scripts/generate_code.py --platform psychopy`
- Psychtoolbox 代码生成：`scripts/generate_code.py --platform psychtoolbox`
- 生成代码一致性验证：`scripts/validate_generated_code.py`

## 示例

```bash
python3 scripts/run_pipeline.py demo/stroop/experiment_spec.yaml --platform psychopy
python3 scripts/run_pipeline.py demo/stroop/experiment_spec.yaml --platform psychtoolbox
```

逆向已有代码：

```bash
python3 scripts/reverse_engineer.py demo/stroop/psychopy/run_experiment.py
```

输出：

```text
demo/stroop/reverse/
  reversed_experiment_spec.yaml
  design_description.md
  reverse_report.md
  llm_prompt.md
```

## 后续扩展方向

- 增加更多 event 类型，例如 mouse response、slider、audio、image、video、eye-tracker trigger。
- 增加 conditions 从 CSV/Excel 导入。
- 增加运行级测试，例如 PsychoPy dry-run 或 Psychtoolbox MATLAB 语法检查。
- 增加“规格完整度评分”和自动追问模板。
