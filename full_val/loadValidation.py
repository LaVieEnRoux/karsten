import numpy as np
import cPickle as pickle
from tidalStats import TidalStats
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from compareData import compareUV, compareTG

# ALTERNATE VERSION FOR ANDY

def dn2dt(datenum):
    return datetime.fromordinal(int(datenum)) + timedelta(days=datenum%1) - \
           timedelta(days=366)

def loadValidation(files):
    '''
    Load validation data into a data struct.

    Takes a dictionary of filenames as input. Keys are run names, values are
    paths to validation structs.
    '''
    # iterate through the runs in the struct
    for run in files:

	# load in struct
	struct_f = open(files[run], 'rb')
	struct = pickle.load(struct_f)

        # iterate through the sites in the run
        for site in struct:

    	    # check if site is a tidegauge site
    	    if (site['type'] != 'TideGauge'):
    	        (elev_suite, speed_suite, dir_suite, u_val, v_val, vel_val) \
		    = compareUV(site)
		site['elev_val'] = elev_suite
    	        site['speed_val'] = speed_suite
    	        site['dir_val'] = dir_suite
		site['u_val'] = u_suite
		site['v_val'] = v_suite
		site['vel_val'] = vel_suite

    	    else:
    	        elev_suite_dg = compareTG(site)
    	        site['tg_val'] = elev_suite_dg
		print 'Tide Gauge loaded'

        filename_out = run + '_val_struct.p'
        out_f = open(filename_out, 'wb')
        pickle.dump(struct, out_f)
	out_f.close()
