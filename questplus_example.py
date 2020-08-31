from psychopy import core, visual, event, monitors, data, gui
import numpy as np
import questplus as qp

# Stimulus domain.
intensities = np.arange(start=-3.5, stop=-0.5+0.25, step=0.25)
stim_domain = dict(intensity=intensities)

# Parameter domain.
thresholds = intensities.copy()
slopes = np.linspace(0.5, 15, 5)
lower_asymptotes = np.linspace(0.01, 0.5, 5)
lapse_rate = 0.01

param_domain = dict(threshold=thresholds,
                    slope=slopes,
                    lower_asymptote=lower_asymptotes,
                    lapse_rate=lapse_rate)

# Outcome (response) domain.
responses = ['Yes', 'No']
outcome_domain = dict(response=responses)

# Further parameters.
func = 'weibull'
stim_scale = 'log10'
stim_selection_method = 'min_entropy'
param_estimation_method = 'mean'

# Initialize the QUEST+ staircase.
q = qp.QuestPlus(stim_domain=stim_domain,
                 func=func,
                 stim_scale=stim_scale,
                 param_domain=param_domain,
                 outcome_domain=outcome_domain,
                 stim_selection_method=stim_selection_method,
                 param_estimation_method=param_estimation_method)

trial_count = 20
for current_trial_number in range(1, trial_count+1):
    next_stim = q.next_stim
    print(f'Please present stimulus {next_stim}.')
    
    # Retrieve response
    # ...
    # outcome = dict(response='Yes')  or
    # outcome = dict(response='No')
    q.update(stim=next_stim, outcome=outcome)

print(f'\nParameter estimates:\n')
for param_name, value in q.param_estimate.items():
    print(f'    {param_name}: {value:.3f}')