import numpy as np
from datetime import datetime, timedelta

def date2py(matlab_datenum):
    python_datetime = datetime.fromordinal(int(matlab_datenum)) + \
        timedelta(days=matlab_datenum%1) - timedelta(days = 366)

    return python_datetime

def py2date(dt):
   mdn = dt + timedelta(days = 366)
   frac_seconds = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
   frac_microseconds = dt.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
   return mdn.toordinal() + frac_seconds + frac_microseconds

def rotate_coords(x, y, theta):
    '''
    Similar to "rotate_to_channelcoords.m" code,
    theta is now the angle
    between the old axis and the new x-axis (CCw is positive)
    '''

    xnew = x * np.cos(theta) + y * np.sin(theta)
    ynew = -x * np.sin(theta) + y * np.cos(theta)

    return xnew, ynew

def get_DirFromN(u,v):
    '''
    #This function computes the direction from North with the output in degrees
    #and measured clockwise from north.
    #
    # Inputs:
    #   u: eastward component
    #   v: northward component
    '''

    theta = np.arctan2(u,v) * 180 / np.pi

    if (theta < 0):
        theta = theta + 360
    return theta

def EnsembleData_FlowFile(t_ens, time, data, pres):
    '''
    Translation of the EnsembleData_FlowFile.m program provided by Justine
    McMillan

    Performs time averaging on the input ADCP data. Allows for nonuniform
    delta t values in input data.

    Inputs:
    - t_ens: ensemble time in seconds (i.e. timestep length for averaging)
    - time, data, pres: fields of Flow Files

    Outputs:
    - time_out, data_out, pres_out: same format as input files (with std
      dev included)
    '''

    # set up outputs
    time_out, data_out, pres_out = {}, {}, {}

    ens_tol = 0.1 # allow for 10% of points to be missing in an ensemble

    # set up time variables
    SEC_TO_DAY = 1. / (24. * 3600.)
    delta_t = np.mean(np.diff(time['mtime'])) / SEC_TO_DAY
    delta_t_1 = (time['mtime'][1] - time['mtime'][0]) / SEC_TO_DAY
    t_ens_day = t_ens * SEC_TO_DAY

    # set start time to start on the hour
    start = date2py(time['mtime'][0])
    yr, mm, dd, hr = start.year, start.month, start.day, start.hour
    new_start = datetime(yr, mm, dd, hr, 0, 0)
    new_start = py2date(new_start)

    # set up time vector
    time_out['mtime'] = np.arange(new_start, time['mtime'][-1], t_ens_day)
    num_pts = time_out['mtime'].size

    # set approximate number of points per output timestep
    pts_approx = float(t_ens) / float(delta_t)

    # initialize output data matrices with NaNs
    pres_out['surf'] = np.nan * np.ones(num_pts)
    pres_out['surf_std'] = np.nan * np.ones(num_pts)
    fields = ['mag_signed_vel','east_vel','north_vel','vert_vel','error_vel',
              'dir_vel']
    n_bins = data['east_vel'].shape[-1]
    for field in fields:
	data_out[field] = np.nan * np.ones((num_pts, n_bins))
	data_out[field + '_std'] = np.nan * np.ones((num_pts, n_bins))

    # iteratively compute means and standard deviations for each interval
    for i in np.arange(num_pts):
	# communicate progress
	if (i % 200 == 0):
	    print 'Ensemble averaging at step {} / {}'.format(i, num_pts)

	t_start = time_out['mtime'][i] - 0.5 * t_ens_day
	t_end = time_out['mtime'][i] + 0.5 * t_ens_day
	index = np.where((time['mtime'] >= t_start) & (time['mtime'] < t_end))[0]

	if (index.size == 0):
	    print 'Empty index!'

	# check if more than 10% of the values are missing
	if (index.size < pts_approx * (1 - ens_tol)):
	    time_out['mtime'][i] = np.nan
	    pres_out['surf'][i] = np.nan
	    pres_out['surf_std'][i] = np.nan
	else:
	    pres_out['surf'][i] = np.nanmean(pres['surf'][index])
	    pres_out['surf_std'][i] = np.nanstd(pres['surf'][index])

	# calculate mean and std for each field
	for field in fields:
	    field_std = field + '_std'

	    # iterate through the bins
	    for z in np.arange(n_bins):

	        # check if more than 10% of the values are missing
	        if (index.size < pts_approx * (1 - ens_tol)):
	    	    data_out[field][i, z] = np.nan
	    	    data_out[field_std][i, z] = np.nan

	        else:
	    	    f_data = data[field]		    

	    	    # compute mean, treat direction separately
	    	    if (field == 'dir_vel'):
	    	        data_out['dir_vel'][i, z] = \
	    		    get_DirFromN(data_out['east_vel'][i, z],
	    			         data_out['north_vel'][i, z])

	    	    else:
	    	        data_out[field][i, z] = np.nanmean(f_data[index, z])
	    		
	    	    # compute standard deviation
	    	    data_out[field_std][i, z] = np.nanstd(f_data[index, z])

    # trim nans at front and end
    nan_index = np.where(~np.isnan(time_out['mtime']))[0]
    time_out['mtime'] = time_out['mtime'][nan_index[0]:nan_index[-1]]
    pres_out['surf'] = pres_out['surf'][nan_index[0]:nan_index[-1]]
    pres_out['surf_std'] = pres_out['surf_std'][nan_index[0]:nan_index[-1]]

    # trim nans from data for each field
    for field in fields:
	field_std = field + '_std'
	data_out[field] = data_out[field][nan_index[0]:nan_index[-1]]
	data_out[field_std] = data_out[field_std][nan_index[0]:nan_index[-1]]

    return time_out, data_out, pres_out
