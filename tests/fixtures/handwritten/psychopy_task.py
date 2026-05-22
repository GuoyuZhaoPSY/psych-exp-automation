from psychopy import core, event, visual
import csv

win = visual.Window([800, 600], fullscr=False)
instruction = visual.TextStim(win, text="Press space when you see X.")
target = visual.TextStim(win, text="X")

instruction.draw()
win.flip()
event.waitKeys(keyList=["space"])

target.draw()
win.flip()
clock = core.Clock()
keys = event.waitKeys(maxWait=1.5, keyList=["space"], timeStamped=clock)
core.wait(0.5)

with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["response", "rt"])
    writer.writeheader()
