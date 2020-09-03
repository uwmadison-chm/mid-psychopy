# -*- coding: utf-8 -*-
"""
MID.py

Monetary incentive delay task with valences for reward/loss and a neutral 
condition, for 5 total trial types.

Presentation times vary based on a staircase procedure calibrated to reach 66% 
success.

A run is currently 30 trials; run orders and fixation timings generated by Jeanette Mumford.
To change run length would require regenerating new order files.

Based on code originally written by @nivreggev, see README
"""
from psychopy import gui, visual, core, data, event, logging, monitors
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER)
from psychopy.hardware.emulator import launchScan
from numpy.random import random, shuffle
import random
import os
import csv
from pathlib import Path

## setting up some user-defined variables

DEBUG = False
expName = "MID"
version = "1.0"
data_dir = "data" # location of outputs to be generated; includes data for participants as well as trial selection and trial presentation sequence
inst_dir = "text" # location of instructions directory
inst_file = ["instructions_MID.txt"] # name of instructions files (needs to be .txt)

num_runs = 3
# Trials per run
num_trials = 30

reward_high = 7
reward_low = 1
loss_high = -7
loss_low = -1

initial_fix_duration = 8 # added time to make sure homogenicity of magnetic field is reached
min_target_dur = 0.16 # sets the minimum presentation time for target (in seconds)
max_target_dur = 0.5
cue_time = 0.25
feedback_time = 2.0
closing_fix_dur = 18 # added time to make sure haemodynamic responses of the last trials are properly modeled

# settings for fMRI emulation:
MR_settings = {
    'TR': 2.000,     # duration (sec) per whole-brain volume
    'volumes': 110,  # number of whole-brain 3D volumes per scanning run
    'sync': 'equal', # character to use as the sync timing event; assumed to come at start of a volume
    'skip': 2,       # number of volumes lacking a sync pulse at start of scan (for T1 stabilization)
    'sound': False
}


## defining some initialization functions

def initialization(expName,version):
    """Present initial dialog; initialize some parameters"""
    # Store info about the experiment session
    expName = expName + version
    expInfo = {
        'participant': '9999',
        'session': '1', 
        'fMRI? (yes or no)': 'no'
    }
    dlg = gui.DlgFromDict(dictionary=expInfo, title=expName)
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    expInfo['date'] = data.getDateStr()  # add a simple timestamp
    expInfo['expName'] = expName
    sn = int(expInfo['participant'])
    session = int(expInfo['participant'])

    # Check for various experimental handles
    if expInfo['fMRI? (yes or no)'].lower() == 'yes':
        fmri = True
    else:
        fmri = False
    return(expInfo,expName,sn,session,fmri)


def make_screen():
    """Generates screen variables"""
    win_res = [1920, 1080]
    exp_mon = monitors.Monitor('exp_mon')
    exp_mon.setSizePix(win_res)
    win = visual.Window(size=win_res, screen=0, allowGUI=True,
                        fullscr=True, monitor=exp_mon, units='height',
                        color="Black")
    return(win_res, win)

def start_datafiles(_thisDir, expName, expInfo, data_dir, sn, fmri):
    """Creates name for datafile (after checking for old one)"""
    pad = 4-len(str(sn))
    snstr = '0'*pad + str(sn)
    fname = expName + '_' + ['behavioral', 'fmri'][fmri] + '_' + snstr
    if os.path.exists(fname):
        if i == fname + '.csv':
            warndlg = gui.Dlg(title='Warning!')
            warndlg.addText('A data file with this number already exists.')
            warndlg.addField('Overwrite?\t\t', initial="no")
            warndlg.addField('If no, new SN:\t', initial='0')
            warndlg.show()
            if gui.OK:
                over = warndlg.data[0].lower() == 'no'
            else:
                core.quit()
            if over:
                sn = int(warndlg.data[1])
                pad = 4-len(str(sn))
                snstr = '0'*pad + str(sn)
                fname = expName + '_'  + ['behavioral', 'fmri'][fmri] + '_' + snstr
    filename = _thisDir + os.sep + data_dir + os.sep + fname
    return(filename)

def display_inst(instr_part,task,forwardKey,backKey,startKeys,instructFinish):
    """ display instructions
    instr_part: instructions extracted from text
    task: task serial number (in actual serial order, starting at 1; convetred to Python's representation, where 1 is 0, in the function"""
    endOfInstructions = False
    instructLine = 0
    inst = instr_part[task-1]
    while not endOfInstructions:
        instructPrompt.setText(inst[instructLine])
        instructPrompt.draw()
        if instructLine == 0:
            instructFirst.draw()
            win.flip()
            instructRep = event.waitKeys(keyList=[forwardKey])
        else:
            instructMove.draw()
            win.flip()
            instructRep = event.waitKeys(keyList=[forwardKey, backKey])
        if instructRep[0] == backKey:
            instructLine -= 1
        elif instructRep[0] == forwardKey:
            instructLine += 1
        if inst[instructLine] == "end":
            endOfInstructions = True

    instructFinish.draw()
    win.flip()
    event.waitKeys(keyList=startKeys)

### START SET UP OF STUDY

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# present initialization dialog
[expInfo,expName,sn,session,fmri] = initialization(expName,version)

# Data file name creation; later add .psyexp, .csv, .log, etc
filename = start_datafiles(_thisDir, expName, expInfo, data_dir, sn, fmri)

# An ExperimentHandler isn't essential but helps with data saving
exp = data.ExperimentHandler(name=expName, version=version, extraInfo=expInfo, runtimeInfo=None,
    originPath=None, savePickle=True, saveWideText=True, dataFileName=filename)

# save a log file for detail verbose info
logFile = logging.LogFile(filename+'.log', level=logging.EXP)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

# Setup the window and presentation constants
[win_res, win] = make_screen()
yScr = 1.
xScr = float(win_res[0])/win_res[1]
fontH = yScr/25
wrapW = xScr/1.5
text_color = 'white'
# store frame rate of monitor if we can measure it
expInfo['frameRate'] = win.getActualFrameRate()
if expInfo['frameRate'] != None and expInfo['frameRate'] < 300:
    frameDur = 1.0 / round(expInfo['frameRate'])
else:
    frameDur = 1.0 / 60.0  # could not measure, so guess

# set random seed - participant and session dependent
random.seed(sn * (session + 1000))

# determine accepted inputs
forwardKey = "2"
backKey = "1"
startKeys = ["enter","equal","return"]
expKeys = ["1","2","3","4","5","6","7","8","9"]

instructFirst = visual.TextStim(win, text=f"Press {forwardKey} to continue.", height=fontH, color=text_color, pos=[0, -yScr/4])
instructMove = visual.TextStim(win, text=f"Press {forwardKey} to continue, or {backKey} to go back.", height=fontH, color=text_color, pos=[0, -yScr/4])

# import instructions
instr_part = [[],[],[]]
for inst in range (0,len(inst_file)):
    inname = _thisDir + os.sep + inst_dir + os.sep + inst_file[inst]
    infile = open(inname, 'r')
    for line in infile:
        instr_part[inst].append(line.rstrip())
    instr_part[inst].append("end")
    infile.close()

## START component code to be run before the window creation

# create fixation stimulus
fix = visual.TextStim(win, pos=[0, 0], text='+', height=fontH*2, color=text_color)
clock = core.Clock()

# Initialize components for Routine "instructions"
instructPrompt = visual.TextStim(win=win, font='Arial', pos=(0, yScr/10), height=fontH, wrapWidth=wrapW, color=text_color);
instructFinish = visual.TextStim(win, text="You have reached the end of the instructions. When you are ready to begin the task, place your fingers on the keys and notify the experimenter.",
                                     height=fontH, color=text_color, pos=[0, 0], wrapWidth=wrapW)

# Initialize components for task transitions
wait = visual.TextStim(win, pos=[0, 0], text="The task will begin momentarily. Get ready...", height=fontH, color=text_color)
wait_str = "The task will begin momentarily. Get ready..."
endf = visual.TextStim(win, pos=[0, 0], text="Thank you. This part of the experiment is now complete.",wrapWidth=wrapW, height=fontH, color=text_color)

# Initialize components for Routine "cue"
cues = {
    'reward.low':  visual.ImageStim(win, size=0.6, image="assets/gain1.png"),
    'reward.high': visual.ImageStim(win, size=0.6, image="assets/gain2.png"),
    'neutral':     visual.ImageStim(win, size=0.6, image="assets/neutral.png"),
    'loss.low':    visual.ImageStim(win, size=0.6, image="assets/loss1.png"),
    'loss.high':   visual.ImageStim(win, size=0.6, image="assets/loss2.png"),
}
CueClock = core.Clock()

# Initialize components for Routine "Target"
TargetClock = core.Clock()
Target = visual.Rect(win,width=0.5, height=0.5, fillColor = "white", lineWidth=0, pos=(0,0))

# Initialize components for Routine "Feedback"
FeedbackClock = core.Clock()
trial_feedback = visual.TextStim(win=win, name='trial_feedback',
    text='Trial:', font='Arial', pos=(0, yScr/6), height=fontH+yScr/20, wrapWidth=None, ori=0,
    color='White', colorSpace='rgb', opacity=1);
exp_feedback = visual.TextStim(win=win, name='exp_feedback',
    text='Total:', font='Arial', pos=(0, -yScr/20), height=fontH+yScr/20, wrapWidth=None, ori=0,
    color='White', colorSpace='rgb', opacity=1);

breakPrompt = visual.TextStim(win, text="Take a break", height=fontH, color=text_color, pos=(0,0))
breakEnd = visual.TextStim(win, text="Get ready", height=fontH, color=text_color, pos=(0,0))

# Create some handy timers
globalClock = core.Clock()  # to track the time since experiment started
runClock = core.Clock()  # to track the time since experiment started
trialClock = core.Clock()  # to track the time since trial started
routineTimer = core.CountdownTimer()  # to track time remaining of each (non-slip) routine

## Displaying Instructions

# keyboard checking is just starting
event.clearEvents(eventType='keyboard')
event.Mouse(visible=False)
display_inst(instr_part,1,forwardKey,backKey,startKeys,instructFinish)

# reset the non-slip timer for next routine
routineTimer.reset()
event.clearEvents(eventType='keyboard')


### PREP EXPERIMENTAL LOOP

# set up counters for trials (to determine stimulus and for total earnings)
trial_counter = 0
total_earnings = 0

# load a list of the possible order files
orders = list(Path(os.path.join(_thisDir, "orders")).glob("*.csv"))
# pick 3 random trial orders without replacement
order_files = random.sample(orders, 3)
    
# create the staircase handler to adjust for individual threshold (stairs defined in units of screen frames; actual minimum presentation duration is determined by the min_target_dur parameter, the staircase procedure can only add frame rates to that minimum value)
trials = data.StairHandler(startVal=13.0,
    stepType='lin',
    stepSizes=[6, 3, 3, 2, 2, 1, 1],  # reduce step size every two reversals
    minVal=0, maxVal=20,
    nUp=1,
    nDown=2, # will home in on the 66% threshold (nUp=1, nDown=3 homes in on 80%)
    nTrials=num_runs * num_trials,
    extraInfo=expInfo)

exp.addLoop(trials) # add the staircaser to the experiment

def show_stim(stim, duration):
    t_start = globalClock.getTime()
    t = t_start
    while t < t_start + float(duration):
        t = globalClock.getTime()
        if stim:
            stim.draw()
        win.flip()

def show_fixation(duration):
    show_stim(fix, duration)


# EXPERIMENT BEGINS

# Loop the rest of this for num_runs
for run in range(0, num_runs):
    order_file = order_files[run]
    order = csv.DictReader(open(order_file))
    order = list(order)
    trials.addOtherData('run.order.file', order_file)
    if DEBUG:
        print(f'order_file is {order_file}')

    # Wait for TR signal if in scanner
    if fmri:
        if DEBUG:
            print("waiting for TR")
        wait.draw()
        win.flip()
        event.waitKeys(keyList=startKeys)
    elif run == 0:
        # launch: operator selects Scan or Test (emulate); see API docuwmentation
        vol = launchScan(win, MR_settings, globalClock=globalClock, wait_msg=wait_str)

    globalClock.reset() # to align actual time with virtual time keeper
    if DEBUG:
        print("actual start {globalClock.getTime()}")

    runClock.reset()
    if DEBUG:
        print(f'run {run + 1} of {num_runs}')

    # present initial fixation on the first run
    if run == 0:
        show_fixation(initial_fix_duration)

    for trial in range(0, num_trials):
        if DEBUG:
            print(f'trial {trial + 1} of {num_trials}')

        trial_duration = trials.next()
        trials.addOtherData('trial.staircase.duration', trial_duration)
        trialClock.reset()

        trials.addOtherData('time.onset', globalClock.getTime()) # add trial onset time to the data file

        trial_details = order[trial_counter]
        trial_type = trial_details['trial.type']

        def log_detail(x):
            print(f"{x}: {trial_details[x]}")
        if DEBUG:
            log_detail('fix.after.cue')
            log_detail('fix.after.stim')
            log_detail('fix.after.feedback')
            log_detail('trial.type')

        trial_counter += 1

        cue = cues[trial_type]

        if DEBUG:
            print('time before cue: ', trialClock.getTime())

        show_stim(cue, cue_time)

        if DEBUG:
            print('time after cue: ', trialClock.getTime())

        show_fixation(trial_details['fix.after.cue'])

        if DEBUG:
            print('time after first fix: ', trialClock.getTime())

        # ------Prepare to start Routine "Target"-------
        t = 0
        TargetClock.reset()  # clock

        # reset the non-slip timer for next routine
        routineTimer.reset()
        continueRoutine = True
        # Maximum time allowed for target response
        routineTimer.add(max_target_dur)

        # update component parameters for each repeat
        target_response = event.BuilderKeyResponse()
        trial_response = 0
        rt = None

        # keep track of which components have finished
        TargetComponents = [Target, target_response]
        for thisComponent in TargetComponents:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED

        # -------Start Routine "Target"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = TargetClock.getTime()

            # selection screen updates
            if t >= 0.0 and Target.status == NOT_STARTED:
                # keep track of start time/frame for later
                Target.tStart = t
                # display target
                Target.setAutoDraw(True)
                # open response options
                target_response.tStart = t
                target_response.status = STARTED
                # keyboard checking is just starting
                win.callOnFlip(target_response.clock.reset)  # t=0 on next screen flip
                event.clearEvents(eventType='keyboard')
                theseKeys = []

            frameRemainsResp = min_target_dur + frameDur * trial_duration
            if Target.status == STARTED and t >= frameRemainsResp:
                if DEBUG:
                    print('trial_duration:',trial_duration)
                    print('frameDur:',frameDur)
                    print('frameRemainsResp:',frameRemainsResp)

                Target.setAutoDraw(False)
                theseKeys = event.getKeys(keyList=expKeys)

                if len(theseKeys) > 0:  # at least one key was pressed
                    trial_response = 1
                    rt = target_response.clock.getTime()
                    target_response.rt = rt

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in TargetComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine: # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # -------Ending Routine "Target"-------
        for thisComponent in TargetComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        if DEBUG:
            print('time after target: ', trialClock.getTime())

        # add the data to the staircase so it can be used to calculate the next level
        trials.addResponse(trial_response)

        # check responses to add RT
        if trial_response:
            trials.addOtherData('target_response.rt', target_response.rt)

        reward = 0

        # update trial components
        if trial_type == 'reward.high':
            if trial_response:
                reward = reward_high
        elif trial_type == 'reward.low':
            if trial_response:
                reward = reward_low
        elif trial_type == 'loss.high':
            if not trial_response:
                reward = loss_high
        elif trial_type == 'loss.low':
            if not trial_response:
                reward = loss_low

        trials.addOtherData('trial.reward', reward)
        total_earnings += reward
        if DEBUG:
            print(f"{trial_type} result: {trial_response}, reward is {reward} for total {total_earnings}" )

        # Fixation after stim target
        show_fixation(trial_details['fix.after.stim'])

        if DEBUG:
            print('time after second fix: ', trialClock.getTime())

        # ------Prepare to start Routine "Feedback"-------
        t = 0
        FeedbackClock.reset()  # clock
        # reset the non-slip timer for next routine
        routineTimer.reset()
        continueRoutine = True
        routineTimer.add(feedback_time)

        def cash_string(r):
            if reward > 0:
                return f"+${reward}.00"
            elif reward < 0:
                return f"-${reward * -1}.00"
            else:
                return f"${reward}.00"

        trial_feedback.setText(cash_string(reward))
        exp_feedback.setText('[' + cash_string(total_earnings) + ']')

        trials.addOtherData('total_earnings', total_earnings)

        # keep track of which components have finished
        FeedbackComponents = [trial_feedback, exp_feedback]
        for thisComponent in FeedbackComponents:
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED

        # -------Start Routine "Feedback"-------
        while continueRoutine and routineTimer.getTime() > 0:
            # get current time
            t = FeedbackClock.getTime()

            # feedback screen updates
            if t >= 0.0 and trial_feedback.status == NOT_STARTED:
                # keep track of start time/frame for later
                trial_feedback.tStart = t
                trial_feedback.setAutoDraw(True)
                exp_feedback.setAutoDraw(True)
            frameRemains = 0.0 + feedback_time - win.monitorFramePeriod * 0.75  # most of one frame period left
            if trial_feedback.status == STARTED and t >= frameRemains:
                trial_feedback.setAutoDraw(False)
                exp_feedback.setAutoDraw(False)

            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in FeedbackComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()

        # -------Ending Routine "Feedback"-------
        for thisComponent in FeedbackComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        if DEBUG:
            print('time after feedback: ', trialClock.getTime())

        # Fixation after stim target
        # We want this to be altered so that the length
        # of the trial is adjusted by the stim difference from 0.5s...

        trial_time = trialClock.getTime()
        fix_after_feedback_adjusted = float(trial_details['fix.after.feedback'])
        if rt:
            difference_between_rt_and_original = max_target_dur - rt
            fix_after_feedback_adjusted += difference_between_rt_and_original
        show_fixation(fix_after_feedback_adjusted)

        if DEBUG:
            print('time after final fix: ', trialClock.getTime())

        # completed trial, add some data to log file
        trials.addOtherData('fix.after.feedback.adjusted', fix_after_feedback_adjusted)
        trials.addOtherData('time.trial', trialClock.getTime())
        trials.addOtherData('time.run', runClock.getTime())
        trials.addOtherData('time.global', globalClock.getTime())
        def add_detail(x):
            trials.addOtherData(x, trial_details[x])
        add_detail('trial.type')
        add_detail('fix.after.cue')
        add_detail('fix.after.stim')
        add_detail('fix.after.feedback')

        # advance to next trial/line in logFile
        exp.nextEntry()

    # completed run
    # present ending fixation (to allow for better evaluation of the last experimental TRs)
    if fmri:
        show_fixation(closing_fix_dur)

    # If we are NOT on the last run, show the break messages
    if run < num_runs - 1:
        show_stim(breakPrompt, 2)
        show_stim(None, 26)
        show_stim(breakEnd, 2)


# completed experimental phase

# end of study message
endf.draw()
win.flip()
event.waitKeys(keyList=startKeys)

logging.flush()
win.close()
core.quit()
