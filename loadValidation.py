import numpy as np
import cPickle as pickle
from tidalStats import TidalStats
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from compareData import compareUV, compareTG
import sys
sys.path.append('/array/home/116822s/github/UTide/')
from utide import ut_reconstr


def dn2dt(datenum):
    return datetime.fromordinal(int(datenum)) + timedelta(days=datenum%1) - \
           timedelta(days=366)

def loadValidation():
    '''
    Load validation data into a data struct.

    NOTE: This is a test version. Final version will take struct as an
          argument.
    '''

    NUM_TIDEGAUGE_KEYS = 15

    # load pickle file
    filename = '/array/home/rkarsten/common_tidal_files/python/wesleyCode/generalRunFiles/structTest2.p'
    struct_f = open(filename, 'rb')
    struct = pickle.load(struct_f)

    # iterate through the runs in the struct
    for run in struct:

        # iterate through the sites in the run
        for site in run:
    
    	    # check if site is a tidegauge site
    	    if (len(site.keys()) != NUM_TIDEGAUGE_KEYS):
    	        (speed_suite, dir_suite) = compareUV(site)
    	        site['speed_val'] = speed_suite
    	        site['dir_val'] = dir_suite
    	    
    	    else:
    	        elev_suite_dg = compareTG(site, 'dg')
    	        elev_suite_gp = compareTG(site, 'gp')
    	        site['dg_elev_val'] = elev_suite_dg
    	        site['gp_elev_val'] = elev_suite_gp

    filename_out = '/array/home/rkarsten/common_tidal_files/python/jonCode/val_struct.pkl'
    out_f = open(filename_out, 'wb')
    pickle.dump(struct, out_f)
'''
    time_series = ut_reconstr(struct[6]['obs_time'], 
			      struct[6]['speed_mod_harmonics'])

    print time_series[0][:20], time_series[1][:20]

    # get data ready for TidalStats
    start = dn2dt(struct[6]['obs_time'][0])
    next = dn2dt(struct[6]['obs_time'][1])
    step = next - start
    time_series = np.asarray(time_series)
    pred_speed = np.sqrt(time_series[0]**2 + time_series[1]**2)

    obs_speed = np.sqrt(struct[6]['obs_timeseries']['u']**2 +
		struct[6]['obs_timeseries']['v']**2)
    obs_speed = np.asarray(obs_speed)

    # print pred_speed[:20], mod_speed[:20]

    test_stats = TidalStats(pred_speed, obs_speed, step, start)

    lr = test_stats.linReg()
    test_stats.plotRegression(lr)
    print lr['r_2'], lr['slope']
    #test_stats.plotData()
    #print test_stats.getStats()
'''

loadValidation()
