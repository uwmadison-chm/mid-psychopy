from psychopy import core, visual, event, monitors, data, gui
import numpy as np

screen = monitors.Monitor('testMonitor')
screen.setSizePix([1680, 1050])
screen.setWidth(47.475)
screen.setDistance(57)
win = visual.Window(allowGUI=True, units='deg', monitor=screen)


grating = visual.GratingStim(win, tex='sin', mask='gauss', contrast=1,
                             sf=3, size=3)

staircase = data.QuestHandler(0.5, 0.2, pThreshold=0.63, gamma=0.01,
                              minVal=0, maxVal=1, ntrials=30)

orientations = [-45, 45]
responses = ['left', 'right']

for contrast in staircase:
    keys = []
    # randomise orientation for this trial
    grating.ori = np.random.choice(orientations)
    # update the difficulty (the contrast)
    grating.contrast = contrast
    # before the trial: wait 500ms
    core.wait(0.5)
    # start the trial: draw grating
    grating.draw()
    win.flip()
    # leave grating on screen for 0.2 seconds
    core.wait(0.2)
    win.flip()
    # wait for response
    while not keys:
        keys = event.getKeys(keyList=['left', 'right'])
    # check if it's the correct response:
    if responses[orientations.index(grating.ori)] in keys:
        response = 1
    else:
        response = 0
    # inform QUEST of the response, needed to calculate next level
    staircase.addResponse(response)

print('The threshold is {s}'.format(s=staircase.mean()))
