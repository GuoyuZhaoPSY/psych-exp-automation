function stroop_color_word()
% Auto-generated from ExperimentSpec.
% Source experiment: 颜色-词 Stroop 任务

KbName('UnifyKeyNames');
Screen('Preference', 'SkipSyncTests', 0);
PsychDefaultSetup(2);

experimentId = 'stroop_color_word';
titleText = '颜色-词 Stroop 任务';
runtime = struct('language', 'zh-CN', 'continue_key', 'space', 'welcome_text', '请根据指导语完成实验。', 'end_text', '实验结束，感谢参与。', 'continue_text', '按空格键继续');
timing = struct('control', 'frame', 'frame_rate_fallback_hz', 60, 'duration_rounding', 'nearest_frame');
conditions = {struct('word', '红', 'ink_color_name', 'red', 'ink_color_rgb', [1 -1 -1], 'congruency', 'congruent', 'correct_key', 'r'), struct('word', '绿', 'ink_color_name', 'green', 'ink_color_rgb', [-1 1 -1], 'congruency', 'congruent', 'correct_key', 'g'), struct('word', '蓝', 'ink_color_name', 'blue', 'ink_color_rgb', [-1 -1 1], 'congruency', 'congruent', 'correct_key', 'b'), struct('word', '黄', 'ink_color_name', 'yellow', 'ink_color_rgb', [1 1 -1], 'congruency', 'congruent', 'correct_key', 'y'), struct('word', '红', 'ink_color_name', 'green', 'ink_color_rgb', [-1 1 -1], 'congruency', 'incongruent', 'correct_key', 'g'), struct('word', '绿', 'ink_color_name', 'blue', 'ink_color_rgb', [-1 -1 1], 'congruency', 'incongruent', 'correct_key', 'b'), struct('word', '蓝', 'ink_color_name', 'yellow', 'ink_color_rgb', [1 1 -1], 'congruency', 'incongruent', 'correct_key', 'y'), struct('word', '黄', 'ink_color_name', 'red', 'ink_color_rgb', [1 -1 -1], 'congruency', 'incongruent', 'correct_key', 'r')};
blocks = {struct('id', 'practice', 'type', 'practice', 'instruction', '练习阶段：请忽略词义，按照墨水颜色按键。红=r，绿=g，蓝=b，黄=y。', 'feedback', true, 'trials', struct('source', 'conditions', 'order', 'random', 'repetitions', 1)), struct('id', 'formal_1', 'type', 'formal', 'instruction', '正式实验开始：规则相同，尽快且准确地反应。', 'feedback', false, 'trials', struct('source', 'conditions', 'order', 'random', 'repetitions', 3))};
trialEvents = {struct('id', 'fixation', 'type', 'text', 'content', '+', 'duration_ms', 500), struct('id', 'stimulus', 'type', 'keyboard_response', 'content', '$trial.word', 'color', '$trial.ink_color_rgb', 'choices', {'r', 'g', 'b', 'y'}, 'correct_key', '$trial.correct_key', 'max_duration_ms', 1500, 'response_ends_trial', true, 'record_response', true), struct('id', 'feedback', 'type', 'feedback', 'show_when', 'block.feedback == true', 'correct_content', '正确', 'incorrect_content', '错误', 'no_response_content', '请更快反应', 'duration_ms', 500), struct('id', 'iti', 'type', 'blank', 'duration_ms', struct('random_uniform', [300 700]))};
dataFields = {'participant_id', 'block_id', 'block_type', 'trial_index_global', 'trial_index_in_block', 'event_id', 'word', 'ink_color_name', 'congruency', 'correct_key', 'response', 'rt', 'correct', 'timestamp'};
outputDirectory = 'data';
filenameTemplate = '{experiment_id}_{participant_id}_{date}.csv';
backgroundColor = [0 0 0];
textColor = [1 1 1];

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

rows = {};
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
                            rows{end + 1} = row; %#ok<AGROW>
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
    filename = strrep(filenameTemplate, '{experiment_id}', experimentId);
    filename = strrep(filename, '{participant_id}', participantId);
    filename = strrep(filename, '{date}', dateText);
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
            key = key{1};
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
    field = fields{i};
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
    key = trialFields{i};
    if ismember(key, fields)
        row.(key) = trial.(key);
    end
end
end

function writeRows(path, fields, rows)
fid = fopen(path, 'w');
fprintf(fid, '%s\n', strjoin(fields, ','));
for r = 1:numel(rows)
    values = cell(1, numel(fields));
    for f = 1:numel(fields)
        value = rows{r}.(fields{f});
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
        values{f} = ['"' value '"'];
    end
    fprintf(fid, '%s\n', strjoin(values, ','));
end
fclose(fid);
end
