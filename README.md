# Monetary Incentive Delay task for PsychoPy

Initially based on Niv Reggev's implementation here: https://osf.io/jkf67/

## About

5 trial types: 10 neutral, 5 high reward, 5 low reward, 5 high loss, 5 low 
loss. Efficient orders calculated by Jeanette Mumford, with jittered fixation.

See `mid.py` for values for reward and loss, and durations for initial 
fixation, cue, feedback, and closing fixation.

Staircases are used for each of the 5 trial types to get close to 66% win 
rate, and dollar values chosen to get close to $50 by end of task.

Intended to be run once outside scanner as a practice to get good staircase 
start values, and N times inside. Different randomly selected orders are 
pulled based on participant ID and session ID.

## Steps

Configured with 3 runs of 30 trials. To run with different lengths of trials 
will require regenerating the files in `orders/`.

### Behavioral run

Run once outside the scanner, setting the participant id, session to "0" and "outside scanner single run for 
staircase?" to "yes".

This will do a "fast" single run with a random order, multiplying fixations by 
`single_speed_factor` (currently 0.25) to speed the run up.

### Scanner run

Set "fMRI?" to "yes", set the participant id, and set the session to "1" (or 
whatever the actual session # is).

Look up the staircase start values from the end of the previous behavioral run log 
(`MID1.0_behavioral_SUBID.log`) and enter them in the matching staircase start boxes.

Total Earnings are at the bottom of the CSV or in the log file.
