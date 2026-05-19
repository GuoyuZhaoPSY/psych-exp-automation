# Contributing

Contributions are welcome, especially from psychology, neuroscience, and human-computer interaction researchers who need practical experiment-building workflows.

## Scope

Good contributions include:

- new generic event types, such as image, audio, video, mouse response, slider, rating scale, or scanner trigger
- stronger validation rules
- better PsychoPy or Psychtoolbox code generation
- documentation for real experiment patterns
- minimal reproducible experiment specs

Avoid contributions that hard-code the system around one classic paradigm. Classic paradigms can be examples, but the core representation should remain generic.

## Required for Code Changes

Every behavior change should include:

- an `ExperimentSpec` fixture or update
- generated-code validation coverage
- a short explanation of timing and data-output implications

Run before submitting:

```bash
python3 -m unittest discover -s tests
```

## Timing Standard

Generated experiment code must control timed visual events by frame count. Convert declared millisecond durations to screen refresh frames, use measured refresh interval when available, and flip once per frame.

For Psychtoolbox, do not disable synchronization tests in generated experiment code.

## Pull Request Style

Keep pull requests small and focused. A useful unit of work is one event type, one backend improvement, or one validation enhancement.
