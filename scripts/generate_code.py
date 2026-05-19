#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from common import ensure_dir, read_spec


def py_literal(value):
    return repr(value)


def sanitize_identifier(value: str) -> str:
    value = re.sub(r"[^0-9a-zA-Z_]+", "_", value)
    if value and value[0].isdigit():
        value = "_" + value
    return value or "experiment"


def psychopy_code(spec: dict) -> str:
    meta = spec["metadata"]
    runtime = spec.get("runtime", {})
    timing = spec.get("timing", {})
    display = spec.get("display", {})
    bg = display.get("background_color", [0, 0, 0])
    text_color = display.get("text_color", [1, 1, 1])
    font_height = float(display.get("font_size", 48)) / 700.0
    conditions = spec.get("conditions", [])
    events = spec["trial_structure"]["events"]
    blocks = spec["blocks"]
    data_fields = spec["data"]["fields"]
    output = spec["output"]

    return f'''#!/usr/bin/env python3
# Auto-generated from ExperimentSpec.
# Source experiment: {meta.get("title")}

from __future__ import annotations

import csv
import os
import random
from datetime import datetime

from psychopy import core, event, gui, visual


EXPERIMENT_ID = {py_literal(meta["experiment_id"])}
TITLE = {py_literal(meta.get("title_zh") or meta["title"])}
RUNTIME = {py_literal(runtime)}
TIMING = {py_literal(timing)}
CONDITIONS = {py_literal(conditions)}
BLOCKS = {py_literal(blocks)}
TRIAL_EVENTS = {py_literal(events)}
DATA_FIELDS = {py_literal(data_fields)}
OUTPUT_DIRECTORY = {py_literal(output["directory"])}
FILENAME_TEMPLATE = {py_literal(output["filename_template"])}
BACKGROUND_COLOR = {py_literal(bg)}
TEXT_COLOR = {py_literal(text_color)}
FONT_HEIGHT = {font_height!r}
FRAME_RATE_FALLBACK_HZ = float(TIMING.get("frame_rate_fallback_hz", 60))


def resolve(value, trial, block):
    if isinstance(value, str) and value.startswith("$"):
        parts = value[1:].split(".")
        root = {{"trial": trial, "block": block}}
        current = root.get(parts[0])
        for key in parts[1:]:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
        return current
    return value


def duration_ms(value):
    if isinstance(value, dict) and "random_uniform" in value:
        low, high = value["random_uniform"]
        return random.uniform(low, high)
    return float(value)


def get_frame_rate(win):
    measured = win.getActualFrameRate(nIdentical=20, nMaxFrames=120, nWarmUpFrames=10, threshold=1)
    return float(measured or FRAME_RATE_FALLBACK_HZ)


def duration_frames(value, frame_rate):
    return max(1, int(round(duration_ms(value) / 1000.0 * frame_rate)))


def draw_text(win, text, color=None):
    stim = visual.TextStim(
        win,
        text=str(text),
        color=color if color is not None else TEXT_COLOR,
        height=FONT_HEIGHT,
        wrapWidth=1.6,
    )
    stim.draw()
    win.flip()


def make_text_stim(win, text, color=None):
    return visual.TextStim(
        win,
        text=str(text),
        color=color if color is not None else TEXT_COLOR,
        height=FONT_HEIGHT,
        wrapWidth=1.6,
    )


def draw_text_for_frames(win, text, color, frames):
    stim = make_text_stim(win, text, color)
    for _ in range(frames):
        stim.draw()
        win.flip()


def blank_for_frames(win, frames):
    for _ in range(frames):
        win.flip()


def keyboard_response_for_frames(win, clock, text, color, choices, frames):
    stim = make_text_stim(win, text, color)
    event.clearEvents(eventType="keyboard")
    response = None
    rt = None
    for frame_index in range(frames):
        stim.draw()
        if frame_index == 0:
            win.callOnFlip(clock.reset)
            win.callOnFlip(event.clearEvents, eventType="keyboard")
        win.flip()
        keys = event.getKeys(keyList=choices, timeStamped=clock)
        if keys:
            response, rt = keys[0][0], keys[0][1] * 1000.0
            break
    return response, rt


def show_instruction(win, text):
    continue_text = RUNTIME.get("continue_text", "按空格键继续")
    continue_key = RUNTIME.get("continue_key", "space")
    draw_text(win, text + "\\n\\n" + continue_text, TEXT_COLOR)
    event.waitKeys(keyList=[continue_key])


def run_experiment():
    info = {{"participant_id": ""}}
    dlg = gui.DlgFromDict(info, title=TITLE)
    if not dlg.OK:
        core.quit()
    participant_id = info.get("participant_id") or "anonymous"

    win = visual.Window(size=[1024, 768], color=BACKGROUND_COLOR, units="height", fullscr=False)
    frame_rate = get_frame_rate(win)
    clock = core.Clock()
    rows = []
    global_index = 0

    show_instruction(win, f"{{TITLE}}\\n\\n{{RUNTIME.get('welcome_text', '请根据指导语完成实验。')}}")

    for block in BLOCKS:
        show_instruction(win, block.get("instruction", ""))
        block_trials = list(CONDITIONS) * int(block["trials"].get("repetitions", 1))
        if block["trials"].get("order") == "random":
            random.shuffle(block_trials)

        for trial_index, trial in enumerate(block_trials, start=1):
            global_index += 1
            last_response = None
            last_rt = None
            last_correct = None

            for ev in TRIAL_EVENTS:
                ev_type = ev["type"]
                if ev_type == "text":
                    frames = duration_frames(ev["duration_ms"], frame_rate)
                    draw_text_for_frames(win, resolve(ev.get("content", ""), trial, block), resolve(ev.get("color"), trial, block), frames)
                elif ev_type == "blank":
                    frames = duration_frames(ev["duration_ms"], frame_rate)
                    blank_for_frames(win, frames)
                elif ev_type == "keyboard_response":
                    content = resolve(ev.get("content", ""), trial, block)
                    color = resolve(ev.get("color"), trial, block)
                    choices = [str(x) for x in ev.get("choices", [])]
                    correct_key = resolve(ev.get("correct_key"), trial, block)
                    frames = duration_frames(ev["max_duration_ms"], frame_rate)
                    last_response, last_rt = keyboard_response_for_frames(win, clock, content, color, choices, frames)
                    last_correct = (last_response == correct_key) if last_response is not None else False
                    if ev.get("record_response", False):
                        row = {{
                            "participant_id": participant_id,
                            "block_id": block.get("id"),
                            "block_type": block.get("type"),
                            "trial_index_global": global_index,
                            "trial_index_in_block": trial_index,
                            "event_id": ev.get("id"),
                            "response": last_response,
                            "rt": last_rt,
                            "correct": last_correct,
                            "timestamp": datetime.now().isoformat(timespec="milliseconds"),
                        }}
                        row.update(trial)
                        rows.append({{field: row.get(field, "") for field in DATA_FIELDS}})
                elif ev_type == "feedback":
                    if block.get("feedback", False):
                        if last_response is None:
                            text = ev.get("no_response_content", "")
                        elif last_correct:
                            text = ev.get("correct_content", "")
                        else:
                            text = ev.get("incorrect_content", "")
                        frames = duration_frames(ev["duration_ms"], frame_rate)
                        draw_text_for_frames(win, text, TEXT_COLOR, frames)
                elif ev_type == "instruction":
                    show_instruction(win, resolve(ev.get("content", ""), trial, block))

    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)
    filename = FILENAME_TEMPLATE.format(
        experiment_id=EXPERIMENT_ID,
        participant_id=participant_id,
        date=datetime.now().strftime("%Y%m%d"),
    )
    path = os.path.join(OUTPUT_DIRECTORY, filename)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=DATA_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    show_instruction(win, RUNTIME.get("end_text", "实验结束，感谢参与。"))
    win.close()
    core.quit()


if __name__ == "__main__":
    run_experiment()
'''


def matlab_literal(value) -> str:
    if isinstance(value, str):
        return "'" + value.replace("'", "''") + "'"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        if all(isinstance(x, (int, float)) for x in value):
            return "[" + " ".join(str(x) for x in value) + "]"
        return "{" + ", ".join(matlab_literal(x) for x in value) + "}"
    if isinstance(value, dict):
        pairs = []
        for k, v in value.items():
            pairs.append(f"{matlab_literal(k)}, {matlab_literal(v)}")
        return "struct(" + ", ".join(pairs) + ")"
    if value is None:
        return "[]"
    return matlab_literal(str(value))


def psychtoolbox_code(spec: dict) -> str:
    meta = spec["metadata"]
    runtime = spec.get("runtime", {})
    timing = spec.get("timing", {})
    function_name = sanitize_identifier(meta["experiment_id"])
    display = spec.get("display", {})
    conditions = spec.get("conditions", [])
    events = spec["trial_structure"]["events"]
    blocks = spec["blocks"]
    data_fields = spec["data"]["fields"]
    output = spec["output"]
    bg = display.get("background_color", [0, 0, 0])
    text_color = display.get("text_color", [1, 1, 1])

    return f'''function {function_name}()
% Auto-generated from ExperimentSpec.
% Source experiment: {meta.get("title")}

KbName('UnifyKeyNames');
Screen('Preference', 'SkipSyncTests', 0);
PsychDefaultSetup(2);

experimentId = {matlab_literal(meta["experiment_id"])};
titleText = {matlab_literal(meta["title"])};
runtime = {matlab_literal(runtime)};
timing = {matlab_literal(timing)};
conditions = {matlab_literal(conditions)};
blocks = {matlab_literal(blocks)};
trialEvents = {matlab_literal(events)};
dataFields = {matlab_literal(data_fields)};
outputDirectory = {matlab_literal(output["directory"])};
filenameTemplate = {matlab_literal(output["filename_template"])};
backgroundColor = {matlab_literal(bg)};
textColor = {matlab_literal(text_color)};

participantId = input('Participant ID: ', 's');
if isempty(participantId)
    participantId = 'anonymous';
end

screens = Screen('Screens');
screenNumber = max(screens);
[win, rect] = PsychImaging('OpenWindow', screenNumber, psychColor(backgroundColor));
ifi = Screen('GetFlipInterval', win);
if isempty(ifi) || ifi <= 0
    ifi = 1 / timing.frame_rate_fallback_hz;
end
Screen('TextSize', win, 48);
HideCursor;

rows = {{}};
globalIndex = 0;

try
    showInstruction(win, rect, [titleText char(10) char(10) runtime.welcome_text], textColor, runtime);
    for b = 1:numel(blocks)
        block = blocks(b);
        showInstruction(win, rect, block.instruction, textColor, runtime);
        blockTrials = repmat(conditions, 1, block.trials.repetitions);
        if strcmp(block.trials.order, 'random')
            blockTrials = blockTrials(randperm(numel(blockTrials)));
        end

        for t = 1:numel(blockTrials)
            trial = blockTrials(t);
            globalIndex = globalIndex + 1;
            lastResponse = '';
            lastRt = NaN;
            lastCorrect = false;

            for e = 1:numel(trialEvents)
                ev = trialEvents(e);
                switch ev.type
                    case 'text'
                        content = resolveValue(ev.content, trial, block);
                        frames = durationFrames(ev.duration_ms, ifi);
                        showTextForFrames(win, rect, content, textColor, frames, ifi);
                    case 'blank'
                        frames = durationFrames(ev.duration_ms, ifi);
                        blankForFrames(win, backgroundColor, frames, ifi);
                    case 'keyboard_response'
                        content = resolveValue(ev.content, trial, block);
                        color = resolveValue(ev.color, trial, block);
                        correctKey = resolveValue(ev.correct_key, trial, block);
                        frames = durationFrames(ev.max_duration_ms, ifi);
                        [lastResponse, lastRt] = collectResponseFrames(win, rect, content, color, ev.choices, frames, ifi);
                        lastCorrect = strcmp(lastResponse, correctKey);
                        if isfield(ev, 'record_response') && ev.record_response
                            row = makeRow(dataFields, participantId, block, trial, ev, globalIndex, t, lastResponse, lastRt, lastCorrect);
                            rows{{end + 1}} = row; %#ok<AGROW>
                        end
                    case 'feedback'
                        if isfield(block, 'feedback') && block.feedback
                            if isempty(lastResponse)
                                fb = ev.no_response_content;
                            elseif lastCorrect
                                fb = ev.correct_content;
                            else
                                fb = ev.incorrect_content;
                            end
                            frames = durationFrames(ev.duration_ms, ifi);
                            showTextForFrames(win, rect, fb, textColor, frames, ifi);
                        end
                end
            end
        end
    end

    if ~exist(outputDirectory, 'dir')
        mkdir(outputDirectory);
    end
    dateText = datestr(now, 'yyyymmdd');
    filename = strrep(filenameTemplate, '{{experiment_id}}', experimentId);
    filename = strrep(filename, '{{participant_id}}', participantId);
    filename = strrep(filename, '{{date}}', dateText);
    writeRows(fullfile(outputDirectory, filename), dataFields, rows);
    showInstruction(win, rect, runtime.end_text, textColor, runtime);
catch ME
    sca;
    ShowCursor;
    rethrow(ME);
end

sca;
ShowCursor;

end

function color = psychColor(value)
if isempty(value)
    color = [255 255 255];
elseif isnumeric(value)
    if max(abs(value)) <= 1
        color = round((value + 1) .* 127.5);
    else
        color = value;
    end
else
    color = [255 255 255];
end
end

function showInstruction(win, rect, textValue, color, runtime)
showText(win, rect, [textValue char(10) char(10) runtime.continue_text], color);
KbWait([], 2);
end

function showText(win, rect, textValue, color)
DrawFormattedText(win, char(string(textValue)), 'center', 'center', psychColor(color));
Screen('Flip', win);
end

function showTextForFrames(win, rect, textValue, color, frames, ifi)
vbl = [];
for frame = 1:frames
    DrawFormattedText(win, char(string(textValue)), 'center', 'center', psychColor(color));
    if frame == 1
        vbl = Screen('Flip', win);
    else
        vbl = Screen('Flip', win, vbl + 0.5 * ifi);
    end
end
end

function blankForFrames(win, backgroundColor, frames, ifi)
vbl = [];
for frame = 1:frames
    Screen('FillRect', win, psychColor(backgroundColor));
    if frame == 1
        vbl = Screen('Flip', win);
    else
        vbl = Screen('Flip', win, vbl + 0.5 * ifi);
    end
end
end

function value = resolveValue(value, trial, block)
if ischar(value) || isstring(value)
    value = char(value);
    if startsWith(value, '$trial.')
        key = erase(value, '$trial.');
        if isfield(trial, key)
            value = trial.(key);
        end
    elseif startsWith(value, '$block.')
        key = erase(value, '$block.');
        if isfield(block, key)
            value = block.(key);
        end
    end
end
end

function frames = durationFrames(value, ifi)
if isstruct(value) && isfield(value, 'random_uniform')
    bounds = value.random_uniform;
    ms = bounds(1) + (bounds(2) - bounds(1)) * rand;
else
    ms = double(value);
end
frames = max(1, round((ms / 1000) / ifi));
end

function [response, rt] = collectResponseFrames(win, rect, textValue, color, choices, frames, ifi)
response = '';
rt = NaN;
startTime = [];
vbl = [];
for frame = 1:frames
    DrawFormattedText(win, char(string(textValue)), 'center', 'center', psychColor(color));
    if frame == 1
        vbl = Screen('Flip', win);
        startTime = vbl;
    else
        vbl = Screen('Flip', win, vbl + 0.5 * ifi);
    end
    [down, secs, keyCode] = KbCheck;
    if down
        key = KbName(find(keyCode, 1));
        if iscell(key)
            key = key{{1}};
        end
        key = lower(key(1));
        if any(strcmp(key, choices))
            response = key;
            rt = (secs - startTime) * 1000;
            KbReleaseWait;
            return;
        end
    end
end
end

function row = makeRow(fields, participantId, block, trial, ev, globalIndex, trialIndex, response, rt, correct)
row = struct();
for i = 1:numel(fields)
    field = fields{{i}};
    row.(field) = '';
end
row.participant_id = participantId;
row.block_id = block.id;
row.block_type = block.type;
row.trial_index_global = globalIndex;
row.trial_index_in_block = trialIndex;
row.event_id = ev.id;
row.response = response;
row.rt = rt;
row.correct = correct;
row.timestamp = datestr(now, 'yyyy-mm-ddTHH:MM:SS.FFF');
trialFields = fieldnames(trial);
for i = 1:numel(trialFields)
    key = trialFields{{i}};
    if ismember(key, fields)
        row.(key) = trial.(key);
    end
end
end

function writeRows(path, fields, rows)
fid = fopen(path, 'w');
fprintf(fid, '%s\\n', strjoin(fields, ','));
for r = 1:numel(rows)
    values = cell(1, numel(fields));
    for f = 1:numel(fields)
        value = rows{{r}}.(fields{{f}});
        if isnumeric(value)
            value = num2str(value);
        elseif islogical(value)
            value = char(string(value));
        elseif iscell(value)
            value = jsonencode(value);
        else
            value = char(string(value));
        end
        value = strrep(value, '"', '""');
        values{{f}} = ['"' value '"'];
    end
    fprintf(fid, '%s\\n', strjoin(values, ','));
end
fclose(fid);
end
'''


def generate(spec: dict, platform: str, out_dir: Path) -> Path:
    ensure_dir(out_dir)
    if platform == "psychopy":
        path = out_dir / "run_experiment.py"
        path.write_text(psychopy_code(spec), encoding="utf-8")
    elif platform == "psychtoolbox":
        function_name = sanitize_identifier(spec["metadata"]["experiment_id"])
        path = out_dir / f"{function_name}.m"
        path.write_text(psychtoolbox_code(spec), encoding="utf-8")
    else:
        raise ValueError(f"Unsupported platform: {platform}")

    (out_dir / "experiment_spec.snapshot.json").write_text(
        json.dumps({k: v for k, v in spec.items() if not k.startswith("_")}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec", type=Path)
    parser.add_argument("--platform", choices=["psychopy", "psychtoolbox"], default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    spec = read_spec(args.spec)
    platform = args.platform or spec["target_platform"]["default"]
    out = args.out or args.spec.parent / platform
    path = generate(spec, platform, out)
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
