# Psych Experiment Automation

English | [中文](README.zh-CN.md)

Psych Experiment Automation helps researchers turn psychology experiment designs into a reproducible, inspectable, and collaborative programming workflow:

1. write or refine an experiment design
2. encode it as `ExperimentSpec` YAML
3. render reviewable Markdown pseudocode
4. generate PsychoPy or Psychtoolbox code
5. validate generated code against the spec

The goal is to lower the coding barrier for psychology, cognitive science, and cognitive neuroscience researchers without forcing experiments into a fixed list of classic paradigms. Names such as Stroop, Flanker, Go/No-Go, and N-back can be useful references, but the system represents experiments as generic `block -> trial -> event` structures.

The project also supports a reverse workflow: existing PsychoPy or Psychtoolbox code can be converted back into a draft YAML spec and a natural-language design description. This is useful for understanding, migrating, or refactoring old experiment scripts.

## Codex-Generated Project

This repository was scaffolded and iteratively generated with Codex by OpenAI. The generated files include the workflow scripts, the installable Codex Skill, the demo experiment, and the validation artifacts. Human review is still required: generated experiment code should be inspected, pilot-tested, and timing-checked on the target machine before real data collection.

## What This Project Does

Instead of asking researchers to write PsychoPy or Psychtoolbox code from scratch, this project lets them describe an experiment in a structured YAML file. The YAML acts as a bridge between research design and executable code.

Benefits:

- makes experiment logic easier to read and discuss
- keeps design, pseudocode, generated code, and validation reports together
- reduces repetitive boilerplate coding
- supports both Chinese and English experiment text
- preserves a machine-checkable source of truth
- encourages frame-level timing control for visual events
- helps recover documentation from existing PsychoPy/Psychtoolbox code

## Core Principles

- `experiment_spec.yaml` is the source of truth.
- One experiment lives in one folder.
- Experiment text can be Chinese, English, or another natural language.
- Timed events are generated with frame-level timing control.
- PsychoPy and Psychtoolbox are the first supported targets.
- Generated code must be inspected, pilot-tested, and verified before real data collection.

## Minimal YAML Example

This is a shortened `ExperimentSpec` example. A full Stroop example is available at [demo/stroop/experiment_spec.yaml](demo/stroop/experiment_spec.yaml).

```yaml
version: "0.1.0"

metadata:
  experiment_id: "simple_reaction_time"
  title: "Simple Reaction Time Task"
  purpose: "Measure response speed to a visual target."

runtime:
  language: "en-US"
  continue_key: "space"
  welcome_text: "Press the key as soon as the target appears."
  end_text: "The experiment is finished. Thank you."
  continue_text: "Press space to continue"

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
    instruction: "Respond as quickly and accurately as possible."
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

## Repository Layout

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

For your own work, create a separate experiment folder:

```text
my_experiment/
  experiment_spec.yaml
  pseudocode.md
  psychopy/
  psychtoolbox/
```

## Quick Start

Run the Stroop demo:

```bash
python3 scripts/run_pipeline.py demo/stroop/experiment_spec.yaml --platform psychopy
python3 scripts/run_pipeline.py demo/stroop/experiment_spec.yaml --platform psychtoolbox
```

This produces or updates:

```text
demo/stroop/pseudocode.md
demo/stroop/psychopy/run_experiment.py
demo/stroop/psychopy/validation_report.md
demo/stroop/psychtoolbox/stroop_color_word.m
demo/stroop/psychtoolbox/validation_report.md
```

## Reverse Engineering

Reverse engineering converts existing code into:

```text
reverse/
  reversed_experiment_spec.yaml
  design_description.md
  reverse_report.md
  llm_prompt.md
```

Run:

```bash
python3 scripts/reverse_engineer.py demo/stroop/psychopy/run_experiment.py
```

The reverse workflow uses this priority:

1. restore from `experiment_spec.snapshot.json` when available
2. recover embedded constants from generated PsychoPy/Psychtoolbox code
3. apply best-effort heuristics to hand-written PsychoPy/Psychtoolbox code

For hand-written code, the generated YAML is a draft. Unknown or ambiguous details are kept as `TODO` items and summarized in `reverse_report.md`. The workflow is meant to support understanding and migration; it cannot guarantee recovery of the original research intent.

## Install as a Codex Skill

Users can ask Codex:

```text
Use skill-installer to install the skill from GuoyuZhaoPSY/psych-exp-automation at skills/psych-exp-automation.
```

Manual installation is also possible:

```bash
mkdir -p ~/.codex/skills
cp -R skills/psych-exp-automation ~/.codex/skills/
```

Restart Codex after installing the skill.

## ExperimentSpec

`ExperimentSpec` is a YAML intermediate representation. English keys are used for machine parsing; values and comments can use the natural language of the experiment.

Important sections:

- `metadata`: experiment id, title, purpose
- `runtime`: language and text shown to participants
- `target_platform`: `psychopy` or `psychtoolbox`
- `design`: variables, levels, randomization, counterbalancing
- `timing`: frame-level timing settings
- `conditions`: trial-level rows
- `trial_structure`: event sequence inside each trial
- `blocks`: block order, repetitions, feedback
- `data`: output fields
- `output`: CSV filename and directory

## Testing

```bash
python3 -m unittest discover -s tests
```

The tests run the Stroop fixture through both supported code generators and validate generated outputs. They do not launch PsychoPy or MATLAB.

## Safety and Scientific Use

This project can speed up programming, but it cannot replace experimental validation. Before collecting real data:

- inspect generated code
- run pilot participants
- verify timing on the target machine
- test data output
- confirm trigger/synchronization behavior for EEG, fMRI, eye tracking, or other external devices

## Contributing

Contributions are welcome:

- new event types, such as image, audio, video, mouse response, slider, rating scale, or scanner trigger
- stronger validation rules
- better PsychoPy or Psychtoolbox backends
- real experiment design examples
- teaching documentation

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).
