# 颜色-词 Stroop 任务 - 结构化伪代码

## 1. 实验概览 / Overview
- 实验 ID / Experiment ID: `stroop_color_word`
- 实验名称 / Title: `颜色-词 Stroop 任务`
- 研究目的 / Purpose: 测量词义自动加工对墨水颜色命名的干扰。
- 参考范式 / Reference: `Stroop; optional label only`（仅作参考，不限制流程）
- 实验呈现语言 / Runtime language: `zh-CN`
- 默认平台 / Default platform: `psychopy`
- 时间控制 / Timing control: `frame`（所有定时事件按屏幕刷新帧控制）

## 2. 全局参数与设计 / Global Design
- 设计类型 / Design type: `within_subject`
- 自变量 / Independent variables:
  - `congruency`: 一致性, levels=['一致', '不一致']
- 因变量 / Dependent variables:
  - `rt`: 反应时, unit=ms
  - `correct`: 正确性, unit=boolean
- 随机化 / Randomization: 每个 block 内随机化 trial 顺序。
- 平衡策略 / Counterbalancing: 本示例不需要额外平衡。

## 3. 实验流程定义 / Procedure
### 3.1 Block 序列 / Block Sequence
- `practice` (practice): source=`conditions`, order=`random`, repetitions=`1`, feedback=`True`
  - 指导语 / Instruction: 练习阶段：请忽略词义，按照墨水颜色按键。红=r，绿=g，蓝=b，黄=y。
- `formal_1` (formal): source=`conditions`, order=`random`, repetitions=`3`, feedback=`False`
  - 指导语 / Instruction: 正式实验开始：规则相同，尽快且准确地反应。

### 3.2 Trial 微观结构 / Trial Events
1. Event `fixation`: type=`text`
   - content: `+`
   - duration_ms: `500`
2. Event `stimulus`: type=`keyboard_response`
   - content: `$trial.word`
   - color: `$trial.ink_color_rgb`
   - max_duration_ms: `1500`
   - choices: `['r', 'g', 'b', 'y']`
   - correct_key: `$trial.correct_key`
3. Event `feedback`: type=`feedback`
   - duration_ms: `500`
   - show_when: `block.feedback == true`
4. Event `iti`: type=`blank`
   - duration_ms: `{'random_uniform': [300, 700]}`

## 4. 数据记录规范 / Data Logging
- `participant_id`
- `block_id`
- `block_type`
- `trial_index_global`
- `trial_index_in_block`
- `event_id`
- `word`
- `ink_color_name`
- `congruency`
- `correct_key`
- `response`
- `rt`
- `correct`
- `timestamp`

## 5. 文件与输出设置 / Output
- format: `csv`
- directory: `data`
- filename_template: `{experiment_id}_{participant_id}_{date}.csv`

[End of Pseudocode]
