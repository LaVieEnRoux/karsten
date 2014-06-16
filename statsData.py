from __future__ import division
import numpy as np
import pandas as pd
import netCDF4 as nc
from datetime import datetime, timedelta
import pickle


def mjd2num(x):

    y = x + 678942

    return y

def closest_point(points, lon, lat):

    point_list = np.array([lon,lat]).T

    closest_dist = ((point_list[:, 0] - points[:, 0, None])**2 +
                    (point_list[:, 1] - points[:, 1, None])**2)

    closest_point_indexes = np.argmin(closest_dist, axis=1)

    return closest_point_indexes

def datetime2matlabdn(dt):
    # ordinal = dt.toordinal()
    mdn = dt + timedelta(days=366)
    frac = (dt-datetime(dt.year, dt.month, dt.day, 0, 0, 0)).seconds / \
        (24.0 * 60.0 * 60.0)
    return mdn.toordinal() + frac


def getData():
    '''
    Extracts data and stores it in a pickle file. I'll write a better
    comment later.
    '''

    # filename = '/home/wesley/github/aidan-projects/grid/dngrid_0001.nc'
    # filename = '/home/abalzer/scratch/standard_run_directory/0.0015/output/dngrid_0001.nc'
    # filename = '/home/wesley/ncfiles/smallcape_force_0001.nc'
    filename = '/home/abalzer/standard_run_directory/0.0015/output/dngrid_0001.nc'
    
    data = nc.Dataset(filename, 'r')
    #x = data.variables['x'][:]
    #y = data.variables['y'][:]
    lon = data.variables['lon'][:]
    lat = data.variables['lat'][:]
    ua = data.variables['ua']
    va = data.variables['va']
    time = data.variables['time'][:]
    #trinodes = data.variables['nv'][:]
    #h = data.variables['zeta'][:]
    
    #(nodexy, uvnodexy, dt, deltat,
    # hour, thour, TP, rho, g, period,
    # nodell, uvnodell, trinodes) = ncdatasort(x, y, time*24*3600,
    #                                          trinodes, lon, lat)
    
    time = mjd2num(time)
    
    #Rayleigh = np.array([1])
    
    # adcpFilename = '/home/wesley/github/karsten/adcp/dngrid_adcp_2012.txt'
    # adcpFilename = '/home/wesley/github/karsten/adcp/testADCP.txt'
    
    adcpFilename = '/home/wesleyb/github/karsten/adcp/dngrid_adcp_2012.txt'
    adcp = pd.read_csv(adcpFilename)
    
    lonlat = np.array([adcp['Longitude'], adcp['Latitude']]).T
    
    index = closest_point(lonlat, lon, lat)
    
    # set up lists for output data, grab shape values
    adcp_out_u, adcp_out_v = [], []
    fvc_out_u, fvc_out_v = [], []

    for i, ii in enumerate(index):
        tmp_path = adcp.iloc[i, -1]
        if tmp_path != 'None':
    	    tmp_adcp = pd.read_csv(tmp_path, index_col=0)
            adcp_size = tmp_adcp['u'].values.size
    
            adcp_out_u.append(np.zeros(adcp_size))
    	    adcp_out_v.append(np.zeros(adcp_size))
        else:
    	    adcp_out_u.append('Nothing!')
    	    adcp_out_v.append('Nothing!')
    
    fvc_out_u, fvc_out_v = np.zeros([index.size, ua[:, 0].size]), \
    		       np.zeros([index.size, ua[:, 0].size])
    adcp_start, adcp_end = [], []
 
    # main loop, loads in data
    for i, ii in enumerate(index):
    
        path = adcp.iloc[i, -1]
        if path != 'None':
            ADCP = pd.read_csv(path, index_col=0)
            ADCP.index = pd.to_datetime(ADCP.index)
   
    	    adcp_out_u[i] = ADCP['u'].values
    	    adcp_out_v[i] = ADCP['v'].values
    	    adcp_start.append(ADCP.index[0].to_datetime())
	    adcp_end.append(ADCP.index[-1].to_datetime())

    	    fvc_out_u[i] = ua[:, ii]
    	    fvc_out_v[i] = va[:, ii]
	else:
	    adcp_start.append('Nothing!')
	    adcp_end.append('Nothing!')
    
    # remove all those 'Nothing's created from empty data
    adcp_out_u = [i for i in adcp_out_u if i != 'Nothing!']
    adcp_out_v = [i for i in adcp_out_v if i != 'Nothing!']
    adcp_start = [i for i in adcp_start if i != 'Nothing!']
    adcp_end = [i for i in adcp_end if i != 'Nothing!']

    # set up times
    f_start = time[0]
    f_end = time[-1]
    f_start = datetime.fromordinal(int(f_start)) + \
	      timedelta(days=(f_start%1)) - timedelta(days=366)
    f_end = datetime.fromordinal(int(f_end)) + timedelta(days=(f_end%1)) - \
	    timedelta(days=366)
    f_step = f_end - f_start

    # put together dictionaries, ready for interpolation/smoothing
    adcp_dicts = []
    fvc_dicts = []
    for i in np.arange(len(adcp_start)):

	print 'Beginning loading into dictionaries'
	print i

	adcp = {}
	adcp['start'] = adcp_start[i]
	adcp['end'] = adcp_end[i]
	adcp['step'] = adcp_end[i] - adcp_start[i]
	adcp['pts'] = np.sqrt(adcp_out_u[i]**2 + adcp_out_v[i]**2)
	adcp_dicts.append(adcp)

	fvc = {}
	fvc['start'] = f_start
	fvc['end'] = f_end
	fvc['step'] = f_step
	fvc['pts'] = np.sqrt(fvc_out_u[i]**2 + fvc_out_v[i]**2)
	fvc_dicts.append(fvc)

    # load data into file using pickle
    filename_1 = '/home/jonsmith/tidal_data/stats_test/ADCP_data1.pkl'
    out_adcp = open(filename_1, 'wb')
    pickle.dump(adcp_dicts, out_adcp)

    print 'File 1 created!'

    filename_2 = '/home/jonsmith/tidal_data/stats_test/FVCOM_data1.pkl'
    out_fvc = open(filename_2, 'wb')
    pickle.dump(fvc_dicts, out_fvc)

    print 'File 2 created!'

    out_adcp.close()
    out_fvc.close()

    print 'Done!'

