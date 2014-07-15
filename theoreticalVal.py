from tidalStats import TidalStats
import numpy as np
from datetime import datetime, timedelta

'''
Create data for use with the TidalStats class to see the effect
of various alterations on skill statistics.
'''

# set up arrays
index = np.arange(0, 50, 0.5)
sine = np.sin(index)
scaled = 2 * sine
shifted = np.roll(sine, 1)
decorrelated = -sine

# grab times
start = datetime.today()
step = timedelta(minutes=10)

# create stats classes
exact = TidalStats(sine, sine, step, start)
scale = TidalStats(sine, scaled, step, start)
shift = TidalStats(sine, shifted, step, start)
decorr = TidalStats(sine, decorrelated, step, start)

# plot the data
exact.plotData(save=False, out_f='plots/exact_test.png')
exact.plotRegression(exact.linReg(), save=False, out_f='plots/exact_lr.png')
print exact.getStats()

scale.plotData(save=False, out_f='plots/scale_test.png')
scale.plotRegression(scale.linReg(), save=False, out_f='plots/scale_lr.png')
print scale.getStats()

shift.plotData(save=False, out_f='plots/shift_test.png')
shift.plotRegression(shift.linReg(), save=False, out_f='plots/shift_lr.png')
print shift.getStats()

decorr.plotData(save=False, out_f='plots/decorr_test.png')
decorr.plotRegression(decorr.linReg(), save=False, out_f='plots/decorr_lr.png')
print decorr.getStats()
