# Psych Experiment Automation

English | [中文](README.zh-CN.md)

Psych Experiment Automation helps researchers turn psychology experiment designs into a reproducible, inspectable, and collaborative programming workflow:

1. write or refine an experiment design
2. encode it as `ExperimentSpec` YAML
3. render reviewable Markdown pseudocode
4. generate PsychoPy or Psychtoolbox code
5. validate generated code against the spec

The goal is to lower the coding barrier for psychology, cognitive science, and cognitive neuroscience researchers without forcing experiments into a fixed list of classic paradigms. Names such as Stroop, Flanker, Go/No-Go, and N-back can be useful references, but the system represents experiments as generic `block -> trial -> event` structures.

## Core Principles

- `experiment_spec.yaml` is the source of truth.
- One experiment lives in one folder.
- Experiment text can be Chinese, English, or another natural language.
- Timed events are generated with frame-level timing control.
- PsychoPy and Psychtoolbox are the first supported targets.
- Generated code must be inspected, pilot-tested, and verified before real data collection.

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

## Install as a Codex Skill

After publishing this repository to GitHub, users can ask Codex:

```text
Use skill-installer to install the skill from <your-name>/psych-exp-automation at skills/psych-exp-automation.
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
