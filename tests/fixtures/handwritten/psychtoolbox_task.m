function psychtoolbox_task()
KbName('UnifyKeyNames');
PsychDefaultSetup(2);
[win, rect] = PsychImaging('OpenWindow', max(Screen('Screens')), [0 0 0]);
DrawFormattedText(win, 'Press space when you see X.', 'center', 'center', [255 255 255]);
Screen('Flip', win);
KbWait;
DrawFormattedText(win, 'X', 'center', 'center', [255 255 255]);
Screen('Flip', win);
startTime = GetSecs;
while GetSecs - startTime < 1.5
    [down, secs, keyCode] = KbCheck;
    if down && keyCode(KbName('space'))
        break;
    end
end
WaitSecs(0.5);
sca;
end
