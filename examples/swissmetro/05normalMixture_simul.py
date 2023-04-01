"""File 05normalMixture_simul.py

:author: Michel Bierlaire, EPFL
:date: Sat Sep  7 18:42:55 2019

 Example of a mixture of logit models, using Monte-Carlo integration, and
 used for simulatiom
 Three alternatives: Train, Car and Swissmetro
 SP data
"""

import sys
import numpy as np
import pandas as pd
import biogeme.database as db
import biogeme.biogeme as bio
from biogeme import models
import biogeme.results as res
from biogeme.expressions import Beta, DefineVariable, bioDraws, MonteCarlo
import matplotlib.pyplot as plt

# Read the data
df = pd.read_csv('swissmetro.dat', sep='\t')
database = db.Database('swissmetro', df)

# The Pandas data structure is available as database.data. Use all the
# Pandas functions to investigate the database. For example:
# print(database.data.describe())

# The following statement allows you to use the names of the variable
# as Python variable.
globals().update(database.variables)

# Removing some observations can be done directly using pandas.
# remove = (((database.data.PURPOSE != 1) &
#           (database.data.PURPOSE != 3)) |
#          (database.data.CHOICE == 0))
# database.data.drop(database.data[remove].index,inplace=True)

# Here we use the "biogeme" way for backward compatibility
exclude = ((PURPOSE != 1) * (PURPOSE != 3) + (CHOICE == 0)) > 0
database.remove(exclude)

# Parameters to be estimated
ASC_CAR = Beta('ASC_CAR', 0, None, None, 0)
ASC_TRAIN = Beta('ASC_TRAIN', 0, None, None, 0)
ASC_SM = Beta('ASC_SM', 0, None, None, 1)
B_COST = Beta('B_COST', 0, None, None, 0)

# Define a random parameter, normally distributed, designed to be used
# for Monte-Carlo simulation
B_TIME = Beta('B_TIME', 0, None, None, 0)

# It is advised not to use 0 as starting value for the following parameter.
B_TIME_S = Beta('B_TIME_S', 1, None, None, 0)
B_TIME_RND = B_TIME + B_TIME_S * bioDraws('B_TIME_RND', 'NORMAL')

# Definition of new variables
SM_COST = SM_CO * (GA == 0)
TRAIN_COST = TRAIN_CO * (GA == 0)

# Definition of new variables: adding columns to the database
CAR_AV_SP = DefineVariable('CAR_AV_SP', CAR_AV * (SP != 0), database)
TRAIN_AV_SP = DefineVariable('TRAIN_AV_SP', TRAIN_AV * (SP != 0), database)
TRAIN_TT_SCALED = DefineVariable('TRAIN_TT_SCALED', TRAIN_TT / 100.0, database)
TRAIN_COST_SCALED = DefineVariable(
    'TRAIN_COST_SCALED', TRAIN_COST / 100, database
)
SM_TT_SCALED = DefineVariable('SM_TT_SCALED', SM_TT / 100.0, database)
SM_COST_SCALED = DefineVariable('SM_COST_SCALED', SM_COST / 100, database)
CAR_TT_SCALED = DefineVariable('CAR_TT_SCALED', CAR_TT / 100, database)
CAR_CO_SCALED = DefineVariable('CAR_CO_SCALED', CAR_CO / 100, database)

# Definition of the utility functions
V1 = ASC_TRAIN + B_TIME_RND * TRAIN_TT_SCALED + B_COST * TRAIN_COST_SCALED
V2 = ASC_SM + B_TIME_RND * SM_TT_SCALED + B_COST * SM_COST_SCALED
V3 = ASC_CAR + B_TIME_RND * CAR_TT_SCALED + B_COST * CAR_CO_SCALED

# Associate utility functions with the numbering of alternatives
V = {1: V1, 2: V2, 3: V3}

# Associate the availability conditions with the alternatives
av = {1: TRAIN_AV_SP, 2: SM_AV, 3: CAR_AV_SP}

# The estimation results are read from the pickle file
try:
    results = res.bioResults(pickleFile='05normalMixture.pickle')
except FileNotFoundError:
    print(
        'Run first the script 05normalMixture.py in order to generate the '
        'file 05normalMixture.pickle.'
    )
    sys.exit()

# Conditional to B_TIME_RND, we have a logit model (called the kernel)
prob = models.logit(V, av, CHOICE)

# We calculate the integration error. Note that this formula assumes
# independent draws, and is not valid for Haltom or antithetic draws.
numberOfDraws = 100000
integral = MonteCarlo(prob)
integralSquare = MonteCarlo(prob * prob)
variance = integralSquare - integral * integral
error = (variance / 2.0) ** 0.5

# And the value of the individual parameters
numerator = MonteCarlo(B_TIME_RND * prob)
denominator = integral

simulate = {
    'Numerator': numerator,
    'Denominator': denominator,
    'Integral': integral,
    'Integration error': error,
}

# Create the Biogeme object
biosim = bio.BIOGEME(database, simulate, numberOfDraws=numberOfDraws)
biosim.modelName = "05normalMixture_simul"

# Simulate the requested quantities. The output is a Pandas data frame
simresults = biosim.simulate(results.getBetaValues())

# 95% confidence interval on the log likelihood.
simresults['left'] = np.log(
    simresults['Integral'] - 1.96 * simresults['Integration error']
)
simresults['right'] = np.log(
    simresults['Integral'] + 1.96 * simresults['Integration error']
)

print(f'Log likelihood: {np.log(simresults["Integral"]).sum()}')
print(
    f'Integration error for {numberOfDraws} draws: '
    f'{simresults["Integration error"].sum()}'
)
print(f'In average {simresults["Integration error"].mean()} per observation.')
print(
    f'95% confidence interval: [{simresults["left"].sum()}-'
    f'{simresults["right"].sum()}]'
)

# Post processing to obtain the individual parameters
simresults['beta'] = simresults['Numerator'] / simresults['Denominator']

# Plot the histogram of individual parameters
simresults['beta'].plot(kind='hist', density=True, bins=20)

# Plot the general distribution of beta
def normalpdf(v, mu=0.0, s=1.0):
    """
    Calculate the pdf of the normal distribution, for plotting purposes.

    """
    d = -(v - mu) * (v - mu)
    n = 2.0 * s * s
    a = d / n
    num = np.exp(a)
    den = s * 2.506628275
    return num / den


betas = results.getBetaValues(['B_TIME', 'B_TIME_S'])
x = np.arange(simresults['beta'].min(), simresults['beta'].max(), 0.01)
plt.plot(x, normalpdf(x, betas['B_TIME'], betas['B_TIME_S']), '-')
plt.show()
