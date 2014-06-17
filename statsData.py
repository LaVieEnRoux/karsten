from __future__ import division
import numpy as np
import pandas as pd
import netCDF4 as nc
from datetime import datetime, timedelta
import pickle
from ut_solv import ut_solv
from ut_reconstr import ut_reconstr

def ncdatasort(x, y, time, trinodes, lon=None, lat=None):

    # Note, when time is passes, it is passed as
    # time*24*3600.
    # Does this need to be done this way?

    hour = 3600
    g = 9.806
    TP = 12.42
    rho = 1026
    period = (TP*3600)/(2*np.pi)

    # time=double(time)
    time = time+678942

    dt = time[1] - time[0]
    thour = time/hour
    deltat = thour[1]-thour[0]

    size = x.shape[0]
    nodexy = np.zeros((size, 2))
    nodexy[:, 0] = x
    nodexy[:, 1] = y
    nodexy = np.array((x, y)).T

    trinodes = trinodes.T-1
    triSize = trinodes.shape[0]
    uvnodexy = np.zeros((triSize, 2))

    uvnodexy[:, 0] = (nodexy[trinodes[:, 0], 0] + nodexy[trinodes[:, 1], 0] +
                      nodexy[trinodes[:, 2], 0]) / 3

    uvnodexy[:, 1] = (nodexy[trinodes[:, 0], 1] + nodexy[trinodes[:, 1], 1] +
                      nodexy[trinodes[:, 2], 1]) / 3

    if lat != None and lon != None:
        nodell = np.array((lon, lat)).T

        uvnodell = np.zeros((triSize, 2))

        uvnodell[:, 0] = (nodell[trinodes[:, 0], 0] +
                          nodell[trinodes[:, 1], 0] +
                          nodell[trinodes[:, 2], 0]) / 3

        uvnodell[:, 1] = (nodell[trinodes[:, 0], 1] +
                          nodell[trinodes[:, 1], 1] +
                          nodell[trinodes[:, 2], 1]) / 3

    else:
        'No nodell, uvnodell set to uvnodexy'
        uvnodell = uvnodexy

    return (nodexy, uvnodexy, dt, deltat, hour, thour,
            TP, rho, g, period, nodell, uvnodell, trinodes)



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
    x = data.variables['x'][:]
    y = data.variables['y'][:]
    lon = data.variables['lon'][:]
    lat = data.variables['lat'][:]
    ua = data.variables['ua']
    va = data.variables['va']
    time = data.variables['time'][:]
    trinodes = data.variables['nv'][:]
    #h = data.variables['zeta'][:]
    
    (nodexy, uvnodexy, dt, deltat,
     hour, thour, TP, rho, g, period,
     nodell, uvnodell, trinodes) = ncdatasort(x, y, time*24*3600,
                                              trinodes, lon, lat)
    
    time = mjd2num(time)
    
    Rayleigh = np.array([1])
    
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
    adcp_start, adcp_end, adcp_step = [], [], []

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
	    adcp_step.append(ADCP.index[1].to_datetime() - adcp_start[i])

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
    f_step = datetime.fromordinal(int(time[1])) + \
	     timedelta(days=(time[1]%1)) - timedelta(days=366) - f_start

    # put together dictionaries, ready for interpolation/smoothing
    adcp_dicts = []
    fvc_dicts = []
    for i in np.arange(len(adcp_start)):
	adcp = {}
	adcp['start'] = adcp_start[i]
	adcp['end'] = adcp_end[i]
	adcp['step'] = adcp_step[i]
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

    filename_2 = '/home/jonsmith/tidal_data/stats_test/FVCOM_data1.pkl'
    out_fvc = open(filename_2, 'wb')
    pickle.dump(fvc_dicts, out_fvc)

    out_adcp.close()
    out_fvc.close()

    # start getting the harmonic data
    new_series = []
    for i in np.arange(len(fvc_dicts)):
        order = ['M2','S2','N2','K2','K1','O1','P1','Q1']
    
        coef = ut_solv(time, ua[:, ii], va[:, ii], uvnodell[ii, 1],
                        cnstit=order, Rayleigh=1, notrend=True, method='ols',
                        nodiagn=True, linci=True, conf_int=False,
                        ordercnstit='frq')
    	    
	# create time array for output time series
	start = adcp_dicts[i]['start']
	step = adcp_dicts[i]['step']
	num_steps = adcp_dicts[i]['pts'].size

	series = start + np.arange(num_steps) * step
	for i, ii in enumerate(series):
	    series[i] = datetime2matlabdn(ii)
    
	# reconstruct the time series using adcp times
	time_series = ut_reconstr(series, coef)
	new_series.append(time_series)
	
    # save harmonic data    
    filename_3 = '/home/jonsmith/tidal_data/stats_test/hindcast_1.pkl'
    out_hind = open(filename_3, 'wb')
    pickle.dump(new_series, out_hind)
    out_hind.close()

    print 'Done!'

getData()
