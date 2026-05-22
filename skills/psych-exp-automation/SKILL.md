---
name: psych-exp-automation
description: Generate psychology experiment specifications, pseudocode, PsychoPy code, and Psychtoolbox code from natural-language experiment designs. Use for arbitrary block/trial/event-based experiments, with frame-level timing and generated-code validation.
---

# Psych Experiment Automation

Use this skill when a user wants to design, specify, generate, reverse engineer, or validate code for a psychology experiment. The workflow is not limited to classic paradigms; represent experiments as generic `blocks`, `trials`, and `events`.

## Core Rules

- `experiment_spec.yaml` is the source of truth.
- Use one folder per experiment; keep generated outputs in that folder.
- Natural language values may be Chinese, English, or another language.
- Platform is selected with `target_platform.default`: `psychopy` or `psychtoolbox`.
- Timed visual events must use frame-level control: convert milliseconds to frame counts and flip once per screen refresh frame.
- Psychtoolbox generation must keep sync tests enabled.
- Reverse engineering is best-effort for hand-written PsychoPy/Psychtoolbox code; keep TODO values when source evidence is missing.
- If information is missing, ask only for details that block programming or validation.

## Experiment Folder Layout

```text
my_experiment/
  experiment_spec.yaml
  pseudocode.md
  psychopy/
    run_experiment.py
    experiment_spec.snapshot.json
    validation_report.md
  psychtoolbox/
    my_experiment_id.m
    experiment_spec.snapshot.json
    validation_report.md
```

## Commands

The bundled scripts are in this skill's `scripts/` directory. Use absolute paths when calling them from another workspace.

Run a full pipeline:

```bash
python3 <skill_dir>/scripts/run_pipeline.py /path/to/my_experiment/experiment_spec.yaml --platform psychopy
python3 <skill_dir>/scripts/run_pipeline.py /path/to/my_experiment/experiment_spec.yaml --platform psychtoolbox
```

Validate only:

```bash
python3 <skill_dir>/scripts/validate_spec.py /path/to/my_experiment/experiment_spec.yaml
```

Reverse engineer existing code:

```bash
python3 <skill_dir>/scripts/reverse_engineer.py /path/to/my_experiment/psychopy/run_experiment.py --platform auto
python3 <skill_dir>/scripts/reverse_engineer.py /path/to/my_experiment/psychtoolbox/my_experiment_id.m --platform auto
```

Reverse outputs are written to `reverse/` in the experiment folder:

```text
reverse/
  reversed_experiment_spec.yaml
  design_description.md
  reverse_report.md
  llm_prompt.md
```

If `reverse_report.md` contains TODO items, read the original code, `reversed_experiment_spec.yaml`, and `reverse_report.md`; only fill fields when the source code provides evidence. Do not invent research intent or design variables.

## Specification Guidance

Required top-level sections:

- `version`
- `metadata`
- `runtime`
- `target_platform`
- `participant`
- `design`
- `display`
- `timing`
- `conditions`
- `trial_structure`
- `blocks`
- `data`
- `output`

Use English keys for parsing. Put the experiment's natural language directly in values such as `title`, `purpose`, `instruction`, `name`, and `levels`. Use YAML comments to explain parameters.

Set:

```yaml
timing:
  control: "frame"
  frame_rate_fallback_hz: 60
  duration_rounding: "nearest_frame"
```

## Clarification Checklist

Before code generation, confirm:

- participant fields
- target platform
- independent variables, dependent variables, and design type
- block order, repetitions, feedback, rest breaks
- trial event order and timing
- stimulus source and condition fields
- response keys and correct-response logic
- data fields and CSV output filename
- trigger or synchronization requirements if EEG, fMRI, eye tracking, or external devices are involved

## References

Read `references/workflow.md` when the user needs more explanation of the project structure or open-source workflow.
