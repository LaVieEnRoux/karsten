import numpy as np
import interpolate
import cPickle as pickle
from tidalStats import TidalStats
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import sys
sys.path.append('/array/home/116822s/github/UTide/')
from utide import ut_reconstr

def loadValidation():
    '''
    Load validation data into a data struct.

    NOTE: This is a test version. Final version will take struct as an
          argument.
    '''

    # load pickle file
    filename = '/array/home/rkarsten/common_tidal_files/python/wesleyCode/generalRunFiles/struct.p'
    struct_f = open(filename, 'rb')
    struct = pickle.load(struct_f)

    print struct[0].items()

    series = ut_reconstr(struct[5]['obs_time'], struct[5]['speed_obs_harmonics'])

    plt.plot(struct[5]['obs_time'], series[0])

loadValidation()
