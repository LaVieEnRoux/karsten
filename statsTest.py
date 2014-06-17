#import numpy as np
from datetime import datetime, timedelta
import pickle
import interpolate
#import smooth
from tidalStats import TidalHeightStats as tideStats
import matplotlib.pyplot as plt

'''
Test of loading in previously saved pickle data, and running it through
interpolation and smoothing functions.
'''

# grab the data
filename_1 = '/home/jonsmith/tidal_data/stats_test/ADCP_data1.pkl'
ADCP_f = open(filename_1, 'rb')
filename_2 = '/home/jonsmith/tidal_data/stats_test/FVCOM_data1.pkl'
FVC_f = open(filename_2, 'rb')
filename_3 = '/home/jonsmith/tidal_data/stats_test/hindcast_1.pkl'
hind_f = open(filename_3, 'rb')

ADCP = pickle.load(ADCP_f)
FVCOM = pickle.load(FVC_f)
hind = pickle.load(hind_f)

# plot the data
#plt.scatter(ADCP[0]['pts'], FVCOM[0]['pts'], c='b')
#plt.show()


# first test
(ADCP_i, FVCOM_i, step, start) = interpolate.interpol(ADCP[0], FVCOM[0], timedelta(minutes=20))

print ADCP_i.size, FVCOM_i.size, step, start

#speed_stats = tideStats(ADCP_i, FVCOM_i, step, start)
#lr = speed_stats.linReg()
#speed_stats.plotRegression(lr)
