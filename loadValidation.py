import numpy as np
import cPickle as pickle
from tidalStats import TidalStats
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from compareData import compareUV, compareTG


def dn2dt(datenum):
    return datetime.fromordinal(int(datenum)) + timedelta(days=datenum%1) - \
           timedelta(days=366)

def loadValidation():
    '''
    Load validation data into a data struct.

    NOTE: This is a test version. Final version will take struct as an
          argument.
    '''

    # load pickle file
    filename = '/array/home/rkarsten/common_tidal_files/python/wesleyCode/generalRunFiles/structTest2.p'
    filename = '/array/home/107002b/github/karsten/generalRunFiles/structStationTest.p'
   lename = '/EcoII/EcoEII_server_data_tree/code/wesCode/project/june_2013_3D_station.p'
    #filename = '/array/home/116822s/2012_run/struct2012_run.p'
    filename = '/EcoII/EcoEII_server_data_tree/code/wesCode/project/june_2013_3D_station.p'
    struct_f = open(filename, 'rb')
    struct = pickle.load(struct_f)

    # iterate through the runs in the struct
    for run in struct.values():

        # iterate through the sites in the run
        for site in run:

    	    # check if site is a tidegauge site
    	    if ('obs_time' in site.keys()):
    	        (elev_suite, speed_suite, dir_suite, u_suite, v_suite, 
		 vel_suite) = compareUV(site)
		site['elev_val'] = elev_suite
    	        site['speed_val'] = speed_suite
    	        site['dir_val'] = dir_suite
		site['u_val'] = u_suite
		site['v_val'] = v_suite
		site['vel_val'] = vel_suite

    	    else:
    	        elev_suite_dg = compareTG(site, 'dg')
    	        elev_suite_gp = compareTG(site, 'gp')
    	        site['dg_elev_val'] = elev_suite_dg
    	        site['gp_elev_val'] = elev_suite_gp

    filename_out = 'val_struct.pkl'
    #filename_out = '/array/home/rkarsten/common_tidal_files/python/jonCode/val_struct_3D.pkl'
    out_f = open(filename_out, 'wb')
    pickle.dump(struct, out_f)
