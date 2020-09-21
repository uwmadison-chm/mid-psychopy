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
from numpy.random import random, shuffle
import random
import os
import csv
import time
from pathlib import Path

## setting up some user-defined variables

DEBUG = False
expName = "MID"
version = "1.0"
data_dir = "data" # location of outputs to be generated; includes data for participants as well as trial selection and trial presentation sequence
inst_dir = "text" # location of instructions directory

num_runs = 3
# Trials per run
num_trials = 30


initial_fix_duration = 8 # added time to make sure homogenicity of magnetic field is reached
min_target_dur = 0.1 # sets the minimum presentation time for target (in seconds)
max_target_dur = 0.5 # maximum presentation of target (in seconds)
cue_time = 2.0 # how long the cue is displayed (in seconds)
feedback_time = 2.0 # how long the trial + total reward feedback is displayed (in seconds)
closing_fix_dur = 18.0 # added time to make sure haemodynamic responses of the last trials are properly modeled

single_speed_factor = 0.25 # how much to multiply fixations by, if doing a single staircase-stabilizing run, to speed it up


total_earnings = 0
total_earnings_goal = 40

reward_high = (5,7)
reward_low = (1,3)
loss_high = (-7,-5)
loss_low = (-3,-1)

def nudge_on_run(r):
    # We nudge on the third run (2 when counting from 0)
    return r == 2


# Attempt to nudge rewards in a direction
def reward_for_range(r, nudge=False):
    if not nudge:
        items = list(range(r[0], r[1]+1))
        return random.choice(items)
    else:
        def distance_to_goal(x):
            return abs(total_earnings + x - total_earnings_goal)

        d0 = distance_to_goal(r[0])
        d1 = distance_to_goal(r[1])

        if d0 < d1:
            return r[0]
        else:
            return r[1]


## defining some initialization functions

def initialization(expName,version):
    """Present initial dialog; initialize some parameters"""
    # Store info about the experiment session
    expName = expName + version
    expInfo = {
        'participant': '9999',
        'session': '1', 
        'fMRI? (yes or no)': 'yes',
        'fMRI reverse screen? (yes or no)': 'yes',
        'outside scanner single run for staircase?': 'no',
        'staircase start reward.low':  '15',
        'staircase start reward.high': '15',
        'staircase start neutral':     '15',
        'staircase start loss.low':    '15',
        'staircase start loss.high':   '15',
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

    if expInfo['fMRI reverse screen? (yes or no)'].lower() == 'yes':
        flipHoriz = True
    else:
        flipHoriz = False

    if expInfo['outside scanner single run for staircase?'].lower() == 'yes':
        single = True
    else:
        single = False

    return(expInfo,expName,sn,session,fmri,single,flipHoriz)


def make_screen():
    """Generates screen variables"""
    if fmri:
        win_res = [800, 600]
        screen=1
    else:
        win_res = [1920, 1080]
        screen=0
    exp_mon = monitors.Monitor('exp_mon')
    exp_mon.setSizePix(win_res)
    
    win = visual.Window(size=win_res, screen=screen, allowGUI=True,
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
    task: task serial numbe"""
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

    print("end of instructions, hit enter to continue")
    instructFinish.draw()
    win.flip()
    event.waitKeys(keyList=startKeys)

### START SET UP OF STUDY

# Ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# present initialization dialog
[expInfo,expName,sn,session,fmri,single,flipHoriz] = initialization(expName,version)

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
    frame_duration = 1.0 / round(expInfo['frameRate'])
else:
    frame_duration = 1.0 / 60.0  # could not measure, so guess

# set random seed - participant and session dependent
random.seed(sn * (session + 1000))

# determine accepted inputs
forwardKey = "2"
backKey = "1"
startKeys = ["enter","equal","return"]
expKeys = ["1","2","3","4","5","6","7","8","9","space"]
escapeKeys = ["escape", "esc"]

if fmri:
    instructFirstText = f"Press button 2 to continue."
    instructMoveText = f"Press button 2 to continue, or button 1 to go back."
    inst_file = ["instructions_MID.txt"]
else:
    instructFirstText = f"Press {forwardKey} to continue."
    instructMoveText = f"Press {forwardKey} to continue, or {backKey} to go back."
    inst_file = ["instructions_MID_outside_scanner.txt"]

instructFirst = visual.TextStim(win, text=instructFirstText, height=fontH, color=text_color, pos=[0, -yScr/4], flipHoriz=flipHoriz)
instructMove = visual.TextStim(win, text=instructMoveText, height=fontH, color=text_color, pos=[0, -yScr/4], flipHoriz=flipHoriz)


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
fix = visual.TextStim(win, pos=[0, 0], text='+', height=fontH*2, color=text_color, flipHoriz=flipHoriz)
clock = core.Clock()

# Initialize components for Routine "instructions"
instructPrompt = visual.TextStim(win=win, font='Arial', pos=(0, yScr/10), height=fontH, wrapWidth=wrapW, color=text_color, flipHoriz=flipHoriz);
if fmri:
    endInstructions = "When you are ready to begin the task, place your finger on any button and notify the experimenter."
else:
    endInstructions = "When you are ready to begin the task, place your fingers on the space bar and hit Enter to begin."

instructFinish = visual.TextStim(win, text=endInstructions,
                                     height=fontH, color=text_color, pos=[0, 0], wrapWidth=wrapW, flipHoriz=flipHoriz)

# Initialize components for task transitions
wait = visual.TextStim(win, pos=[0, 0], text="The task will begin momentarily. Get ready...", height=fontH, color=text_color, flipHoriz=flipHoriz)
endf = visual.TextStim(win, pos=[0, 0], text="Thank you. This part of the experiment is now complete.",wrapWidth=wrapW, height=fontH, color=text_color, flipHoriz=flipHoriz)

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
    text='Trial:', font='Arial', pos=(0, yScr/16), height=fontH+yScr/20, wrapWidth=None, ori=0,
    color='White', colorSpace='rgb', opacity=1, flipHoriz=flipHoriz);
exp_feedback = visual.TextStim(win=win, name='exp_feedback',
    text='Total:', font='Arial', pos=(0, -yScr/16), height=fontH+yScr/20, wrapWidth=None, ori=0,
    color='White', colorSpace='rgb', opacity=1, flipHoriz=flipHoriz);

breakPrompt = visual.TextStim(win, text="Take a break", height=fontH, color=text_color, pos=(0,0), flipHoriz=flipHoriz)
breakEnd = visual.TextStim(win, text="Get ready", height=fontH, color=text_color, pos=(0,0), flipHoriz=flipHoriz)

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
print("instructions complete, continuing")

# reset the non-slip timer for next routine
routineTimer.reset()
event.clearEvents(eventType='keyboard')


### PREP EXPERIMENTAL LOOP

# load a list of the possible order files
orders = list(Path(os.path.join(_thisDir, "orders")).glob("*.csv"))
# pick 3 random trial orders without replacement
order_files = random.sample(orders, 3)
    
# create the staircase handlers to adjust for individual threshold
# (stairs defined in units of screen frames; actual minimum presentation
# duration is determined by the min_target_dur parameter, the staircase 
# procedure can only add frame rates to that minimum value)


if single:
    # Single mode to get the staircase numbers for the scanner run
    num_runs = 1
    stepSizes = [6, 3, 3, 2, 2, 1, 1]
else:
    # Scanner run, needs less adjustment
    stepSizes = [2, 2, 1, 1]


def make_stairs(nTrials, startVal=15.0):
    return data.StairHandler(startVal=startVal,
        stepType='lin',
        stepSizes=stepSizes,
        minVal=0, maxVal=30,
        nUp=1,
        nDown=2, # will home in on the 66% threshold (nUp=1, nDown=3 homes in on 80%)
        nTrials=nTrials,
        extraInfo=expInfo)

perStim = num_runs * num_trials / 6

stairs = {
    'loss.high':   make_stairs(perStim,     int(expInfo['staircase start loss.high'])),
    'loss.low':    make_stairs(perStim,     int(expInfo['staircase start loss.low'])),
    'neutral':     make_stairs(perStim * 2, int(expInfo['staircase start neutral'])),
    'reward.high': make_stairs(perStim,     int(expInfo['staircase start reward.high'])),
    'reward.low':  make_stairs(perStim,     int(expInfo['staircase start reward.low'])),
    }
staircase_end = {}

def get_keypress():
    keys = event.getKeys()
    if keys:
        return keys[0]
    return None

def shutdown():
    print("Logging staircase end values and exiting...")
    stairs = ['loss.high', 'loss.low', 'neutral', 'reward.high', 'reward.low']
    for k in stairs:
        v = staircase_end.get(k, 15)
        logging.warning(f"Staircase end value for {k}: {v}")

    logging.warning(f"Total earnings: {total_earnings}")

    logging.flush()
    win.close()
    core.quit()

def show_stim(stim, duration):
    duration = float(duration)
    t_start = globalClock.getTime()
    routineTimer.reset()
    routineTimer.add(duration)
    event.clearEvents(eventType='keyboard')
    rt = None
    while routineTimer.getTime() > 0:
        key = get_keypress()
        if key and key.lower() in escapeKeys:
            logging.warning("Escape pressed, exiting early!")
            shutdown()
        if not rt and key in expKeys:
            rt = duration - routineTimer.getTime()
        if stim:
            stim.draw()
        win.flip()
    return rt
        

def show_fixation(duration):
    return show_stim(fix, duration)


# EXPERIMENT BEGINS
trial_number = 0

def speed_up(duration):
    return float(duration) * single_speed_factor

# Loop the rest of this for num_runs
for run in range(0, num_runs):
    order_file = order_files[run]
    order = csv.DictReader(open(order_file))
    order = list(order)
    exp.addData('run.order.file', order_file)
    if DEBUG:
        print(f'order_file is {order_file}')

    # Wait for TR signal if in scanner
    if fmri:
        print("waiting for TR, or hit enter at same time as scan starts")
        wait.draw()
        win.flip()
        event.waitKeys(keyList=startKeys)

    print("starting run {run + 1} of {num_runs}")

    runClock.reset()
    if run == 0:
        globalClock.reset() # to align actual time with virtual time keeper
    exp.addData('run.system.seconds_since_epoch', time.time())
    exp.addData('run.system.time', time.asctime())
    exp.nextEntry()

    if DEBUG:
        print(f"actual start {globalClock.getTime()}")

    # present initial fixation
    if single:
        initial_fix_duration = speed_up(initial_fix_duration)
    show_fixation(initial_fix_duration)

    for trial in range(0, num_trials):
        if DEBUG:
            print(f'trial {trial + 1} of {num_trials}')

        # Total trial number along all runs
        trial_number += 1
        trial_details = order[trial]
        trial_type = trial_details['trial.type']

        trial_stairs = stairs[trial_type]

        trial_duration_frames = trial_stairs.next()
        staircase_end[trial_type] = trial_duration_frames

        exp.addData('trial.staircase.durationFrames', trial_duration_frames)
        exp.addData('trial.staircase.thisTrialN', trial_stairs.thisTrialN)

        exp.addData('trial.system.seconds_since_epoch', time.time())
        exp.addData('trial.system.time', time.asctime())

        trialClock.reset()

        exp.addData('trial.number', trial_number)
        exp.addData('time.onset', globalClock.getTime())


        def log_detail(x):
            print(f"{x}: {trial_details[x]}")
        if DEBUG:
            log_detail('fix.after.cue')
            log_detail('fix.after.stim')
            log_detail('fix.after.feedback')
            log_detail('trial.type')

        cue = cues[trial_type]

        if DEBUG:
            print('time before cue: ', trialClock.getTime())

        cue_rt = show_stim(cue, cue_time)
        if cue_rt:
            exp.addData('trial.cue_rt', cue_rt)

        if DEBUG:
            print('time after cue: ', trialClock.getTime())

        fix_after_cue = trial_details['fix.after.cue']
        if single:
            fix_after_cue = speed_up(fix_after_cue)
        too_fast_rt = show_fixation(fix_after_cue)
        if too_fast_rt:
            exp.addData('trial.too_fast_rt', too_fast_rt)

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
                stim_duration = min_target_dur + frame_duration * trial_duration_frames
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

            stim_duration = min_target_dur + frame_duration * trial_duration_frames
            if Target.status == STARTED and t >= stim_duration:
                if DEBUG:
                    print('trial_duration_frames:', trial_duration_frames)
                    print('frame_duration:', frame_duration)
                    print('stim_duration:', stim_duration)

                Target.setAutoDraw(False)
                theseKeys = event.getKeys(keyList=expKeys)

                if len(theseKeys) > 0:  # at least one key was pressed
                    trial_response = 1
                    rt = target_response.clock.getTime()
                    target_response.rt = rt

            # check if all components have finished
            if not continueRoutine:
                break
            continueRoutine = False
            for thisComponent in TargetComponents:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished

            # draw fixation if we're done, so we don't leave a blank screen for any frames
            if not continueRoutine:
                fix.draw()
            win.flip()

        # -------Ending Routine "Target"-------
        for thisComponent in TargetComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)

        if DEBUG:
            print('time after target: ', trialClock.getTime())

        if (cue_rt or too_fast_rt) and trial_response:
            # Fail them if they are button mashing too early
            trial_response = 0
            print("response: too fast")

        # add the data to the current staircase so it can be used to calculate the next level
        trial_stairs.addResponse(trial_response)
        exp.addData("trial.response", trial_response)
        exp.addData('trial.staircase_stim_duration', stim_duration)

        # check responses to add RT
        if trial_response:
            exp.addData('trial.rt', target_response.rt)
            exp.addData('trial.stim_duration', target_response.rt)
            print(f"response: {target_response.rt}")
        else:
            exp.addData('trial.stim_duration', stim_duration)
            print(f"response: none")

        reward = 0
        nudge_reward = nudge_on_run(run)
        exp.addData('trial.nudge_reward', nudge_reward)

        # update trial components
        if trial_type == 'reward.high':
            if trial_response:
                reward = reward_for_range(reward_high, nudge_reward)
        elif trial_type == 'reward.low':
            if trial_response:
                reward = reward_for_range(reward_low, nudge_reward)
        elif trial_type == 'loss.high':
            if not trial_response:
                reward = reward_for_range(loss_high, nudge_reward)
        elif trial_type == 'loss.low':
            if not trial_response:
                reward = reward_for_range(loss_low, nudge_reward)

        exp.addData('trial.reward', reward)
        total_earnings += reward
        if DEBUG:
            print(f"{trial_type} result: {trial_response}, reward is {reward} for total {total_earnings}" )

        # Fixation after stim target
        fix_after_stim = trial_details['fix.after.stim']
        if single:
            fix_after_stim = speed_up(fix_after_stim)
        too_slow_rt = show_fixation(fix_after_stim)
        if too_slow_rt:
            print("response: too slow")
            exp.addData('trial.too_slow_rt', too_slow_rt)

        if DEBUG:
            print('time after second fix: ', trialClock.getTime())

        # ------Prepare to start Routine "Feedback"-------
        t = 0
        FeedbackClock.reset()  # clock
        # reset the non-slip timer for next routine
        routineTimer.reset()
        continueRoutine = True
        routineTimer.add(feedback_time)

        def trial_cash_string(r):
            if r > 0:
                return f"+${r}.00"
            elif r < 0:
                return f"-${r * -1}.00"
            else:
                return f"${r}.00"

        def total_cash_string(r):
            if r < 0:
                return f"-${r * -1}.00"
            else:
                return f"${r}.00"

        trial_feedback.setText(trial_cash_string(reward))
        exp_feedback.setText('[' + total_cash_string(total_earnings) + ']')

        exp.addData('total_earnings', total_earnings)

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
            if not continueRoutine:
                break
            continueRoutine = False
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
        if single:
            fix_after_feedback_adjusted = speed_up(fix_after_feedback_adjusted)
        show_fixation(fix_after_feedback_adjusted)

        if DEBUG:
            print('time after final fix: ', trialClock.getTime())

        # completed trial, add some data to log file
        exp.addData('fix.after.feedback.adjusted', fix_after_feedback_adjusted)
        exp.addData('time.trial', trialClock.getTime())
        exp.addData('time.run', runClock.getTime())
        exp.addData('time.global', globalClock.getTime())
        def add_detail(x):
            exp.addData(x, trial_details[x])
        add_detail('trial.type')
        add_detail('fix.after.cue')
        add_detail('fix.after.stim')
        add_detail('fix.after.feedback')

        # advance to next trial/line in logFile
        exp.nextEntry()

    # completed run
    # present ending fixation (to allow for better evaluation of the last experimental TRs)
    if fmri and not single:
        show_fixation(closing_fix_dur)

    # If we are NOT on the last run, show the break messages
    if run < num_runs - 1:
        show_stim(breakPrompt, 2)
        show_stim(None, 26)
        show_stim(breakEnd, 2)


# completed experimental phase

# end of task message
endf.draw()
win.flip()
print("end of task reached, hit enter to save results and close") 
event.waitKeys(keyList=startKeys)

shutdown()
