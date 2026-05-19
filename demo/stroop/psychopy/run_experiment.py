#!/usr/bin/env python3
# Auto-generated from ExperimentSpec.
# Source experiment: 颜色-词 Stroop 任务

from __future__ import annotations

import csv
import os
import random
from datetime import datetime

from psychopy import core, event, gui, visual


EXPERIMENT_ID = 'stroop_color_word'
TITLE = '颜色-词 Stroop 任务'
RUNTIME = {'language': 'zh-CN', 'continue_key': 'space', 'welcome_text': '请根据指导语完成实验。', 'end_text': '实验结束，感谢参与。', 'continue_text': '按空格键继续'}
TIMING = {'control': 'frame', 'frame_rate_fallback_hz': 60, 'duration_rounding': 'nearest_frame'}
CONDITIONS = [{'word': '红', 'ink_color_name': 'red', 'ink_color_rgb': [1, -1, -1], 'congruency': 'congruent', 'correct_key': 'r'}, {'word': '绿', 'ink_color_name': 'green', 'ink_color_rgb': [-1, 1, -1], 'congruency': 'congruent', 'correct_key': 'g'}, {'word': '蓝', 'ink_color_name': 'blue', 'ink_color_rgb': [-1, -1, 1], 'congruency': 'congruent', 'correct_key': 'b'}, {'word': '黄', 'ink_color_name': 'yellow', 'ink_color_rgb': [1, 1, -1], 'congruency': 'congruent', 'correct_key': 'y'}, {'word': '红', 'ink_color_name': 'green', 'ink_color_rgb': [-1, 1, -1], 'congruency': 'incongruent', 'correct_key': 'g'}, {'word': '绿', 'ink_color_name': 'blue', 'ink_color_rgb': [-1, -1, 1], 'congruency': 'incongruent', 'correct_key': 'b'}, {'word': '蓝', 'ink_color_name': 'yellow', 'ink_color_rgb': [1, 1, -1], 'congruency': 'incongruent', 'correct_key': 'y'}, {'word': '黄', 'ink_color_name': 'red', 'ink_color_rgb': [1, -1, -1], 'congruency': 'incongruent', 'correct_key': 'r'}]
BLOCKS = [{'id': 'practice', 'type': 'practice', 'instruction': '练习阶段：请忽略词义，按照墨水颜色按键。红=r，绿=g，蓝=b，黄=y。', 'feedback': True, 'trials': {'source': 'conditions', 'order': 'random', 'repetitions': 1}}, {'id': 'formal_1', 'type': 'formal', 'instruction': '正式实验开始：规则相同，尽快且准确地反应。', 'feedback': False, 'trials': {'source': 'conditions', 'order': 'random', 'repetitions': 3}}]
TRIAL_EVENTS = [{'id': 'fixation', 'type': 'text', 'content': '+', 'duration_ms': 500}, {'id': 'stimulus', 'type': 'keyboard_response', 'content': '$trial.word', 'color': '$trial.ink_color_rgb', 'choices': ['r', 'g', 'b', 'y'], 'correct_key': '$trial.correct_key', 'max_duration_ms': 1500, 'response_ends_trial': True, 'record_response': True}, {'id': 'feedback', 'type': 'feedback', 'show_when': 'block.feedback == true', 'correct_content': '正确', 'incorrect_content': '错误', 'no_response_content': '请更快反应', 'duration_ms': 500}, {'id': 'iti', 'type': 'blank', 'duration_ms': {'random_uniform': [300, 700]}}]
DATA_FIELDS = ['participant_id', 'block_id', 'block_type', 'trial_index_global', 'trial_index_in_block', 'event_id', 'word', 'ink_color_name', 'congruency', 'correct_key', 'response', 'rt', 'correct', 'timestamp']
OUTPUT_DIRECTORY = 'data'
FILENAME_TEMPLATE = '{experiment_id}_{participant_id}_{date}.csv'
BACKGROUND_COLOR = [0, 0, 0]
TEXT_COLOR = [1, 1, 1]
FONT_HEIGHT = 0.06857142857142857
FRAME_RATE_FALLBACK_HZ = float(TIMING.get("frame_rate_fallback_hz", 60))


def resolve(value, trial, block):
    if isinstance(value, str) and value.startswith("$"):
        parts = value[1:].split(".")
        root = {"trial": trial, "block": block}
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
    draw_text(win, text + "\n\n" + continue_text, TEXT_COLOR)
    event.waitKeys(keyList=[continue_key])


def run_experiment():
    info = {"participant_id": ""}
    dlg = gui.DlgFromDict(info, title=TITLE)
    if not dlg.OK:
        core.quit()
    participant_id = info.get("participant_id") or "anonymous"

    win = visual.Window(size=[1024, 768], color=BACKGROUND_COLOR, units="height", fullscr=False)
    frame_rate = get_frame_rate(win)
    clock = core.Clock()
    rows = []
    global_index = 0

    show_instruction(win, f"{TITLE}\n\n{RUNTIME.get('welcome_text', '请根据指导语完成实验。')}")

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
                        row = {
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
                        }
                        row.update(trial)
                        rows.append({field: row.get(field, "") for field in DATA_FIELDS})
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
