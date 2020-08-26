from __future__ import print_function
from builtins import next
from builtins import range
from psychopy import visual, core, data, event
from numpy.random import shuffle
import copy, time #from the std python libs

conditions=[
    {'label':'gain', 'startVal': 1.0, 'ori':45},
    {'label':'loss','startVal': 1.0, 'ori':45},
    {'label':'neutral', 'startVal': 1.0, 'ori':90},
    ]

stairs = data.MultiStairHandler(conditions=conditions, nTrials=100)

for thisIntensity, thisCondition in stairs:
    thisOri = thisCondition['ori']

    # do something with thisIntensity and thisOri

    stairs.addResponse(correctIncorrect)  # this is ESSENTIAL

# save data as multiple formats
stairs.saveDataAsExcel(fileName)  # easy to browse
stairs.saveAsPickle(fileName)  # contains more info
