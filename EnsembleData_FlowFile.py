import numpy as np
from datetime import datetime, timedelta
from save_FlowFile_BPFormat import get_DirFromN

def date2py(matlab_datenum):
    python_datetime = datetime.fromordinal(int(matlab_datenum)) + \
        timedelta(days=matlab_datenum%1) - timedelta(days = 366)

    return python_datetime

def py2date(dt):
   mdn = dt + timedelta(days = 366)
   frac_seconds = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
   frac_microseconds = dt.microsecond / (24.0 * 60.0 * 60.0 * 1000000.0)
   return mdn.toordinal() + frac_seconds + frac_microseconds

def EnsembleData_FlowFile(t_ens, time, data, pres):
    '''
    Translation of the EnsembleData_FlowFile.m program provided by Justine
    McMillan

    Performs time averaging on the input ADCP data. Allows for nonuniform
    delta t values in input data.

    Inputs:
    - t_ens: ensemble time in seconds
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
    delta_t = mean(diff(time['mtime']) / SEC_2_DAY
    delta_t_1 = (time['mtime'][1] - time['mtime'][0]) / SEC_2_DAY
    t_ens_day = t_ens * SEC_2_DAY

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
              'dir_vel','Ualong','Ucross']
    n_bins = data['east_vel'].shape[-1]
    for field in fields:
	data_out[field] = np.nan * ones(num_pts, n_bins)
	data_out[field + '_std'] = np.nan * ones(num_pts, n_bins)

    # iteratively compute means and standard deviations for each interval
    for i in np.arange(num_pts):
	t_start = time_out['mtime'][i] - 0.5 * t_ens_day
	t_end = time_out['mtime'][i] + 0.5 * t_ens_day
	index = np.where(time['mtime'] >= t_start & time['mtime'] < t_end)[0]
	
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

	    # check if more than 10% of the values are missing
	    if (index.size < pts_approx * (1 - ens_tol)):
		data_out[field][i, :] = np.nan
		data_out[field_std][i, :] = np.nan

	    else:
		# make sure we're not using Ucross or Ualong
		if (field != 'Ucross' & field != 'Ualong'):
		    f_data = data[field]		    

		    # compute mean, treat direction separately
		    if (field == 'dir_vel'):
			data_out['dir_vel'][i, :] = \
			    get_DirFromN(data_out['east_vel'][i, :],
			    		 data_out['north_vel'][i, :])

		    else:
			data_out[field][i, :] = np.nanmean(f_data[index, :])
			
		    # compute standard deviation
		    data_out[field_std][i, :] = np.nanstd(f_data[index, :])
