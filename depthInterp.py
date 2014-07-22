import numpy as np
from scipy.interpolate import interp1d

# ASSUMPTIONS:
# first dimension of matrices identify the timestep, second the depth
# column vectors are organized from bottom to top
# siglay is an array of numbers from 0 to 1 representing percentages


def depthToSigma(obs_data, obs_depth, siglay):
    '''
    Performs linear interpolation on 3D ADCP data to change it into a sigma
    layer format, similar to an FVCOM run.

    Outputs a 2D numpy array representing the ADCP data in sigma layer
    format.
    '''

    ADCP_TOP_SURF = 0.95

    sig_obs = np.zeros(obs_data.shape[0], siglay.size)

    # loop through columns/steps
    for i, column in enumerate(obs_data):

	col_nonan = column[np.where(~np.isnan(column))[0]]

	# map old depths to between 0 and 1, make interpolation function
	old_depths = np.arange(0, obs_depth[i] * ADCP_TOP_SURF, 
		     1. / col_nonan.size)
	mapped_depths = old_depths / obs_depth[i]
	f_obs = interp1d(col_nonan, mapped_depths)

	# perform interpolation
	sig_obs[i] = f_obs(siglay)

    return sig_obs

def sigmaToDepth(mod_data, mod_depth, siglay,
		 obs_data, obs_depth):

def depthFromSurf(mod_data, mod_depth, siglay, 
		  obs_data, obs_depth, depth=5):
    '''
    Performs linear interpolation on 3D ocean data to obtain data at a
    specific distance from the surface.

    Input variables:
	mod_data   2D numpy array of FVCOM model data
	mod_depth  1D numpy array of model depths at each timestep
	siglay     array containing values between 0 and 1 representing the
		   respective percentage of depths for each sigma layer
	obs_data   2D numpy array of observed ADCP data
	obs_depth  1D numpy array of observed depths at each timestep
	depth      number of metres from surface of output timeseries. Defaults
	           to 5m

    Outputs two timeseries representing model and observed data at 'depth'
    metres from the surface.
    '''

    ADCP_TOP_SURF = 0.95

    new_mod = np.zeros(mod_data.shape[0])
    new_obs = np.zeros(obs_data.shape[0])

    # loop over mod_data columns
    for i, step in enumerate(mod_data):

        # create interpolation function
	f_mod = interp1d(step, siglay) # making some assumptions about siglay here

	# find location of specified depth
	location = mod_depth[i] - depth
	sig_loc = float(location) / float(mod_depth[i])

	# perform interpolation to get new data
	new_mod[i] = f_mod(sig_loc)

    # loop over obs_data columns
    for ii, column in enumerate(obs_data):

	# remove nans at the top
	col_nonan = column[np.where(~np.isnan(column))[0]]

	# create interpolation function
	top_depth = ADCP_TOP_SURF * obs_depth[ii]
	index = np.arange(0, top_depth, 1. / col_nonan.size)
	f_obs = interp1d(column, index)

	# find location of specified depth
	location = obs_depth[ii] - depth

	# perform interpolation to get new data
	new_obs[i] = f_obs(location)

    return (new_mod, new_obs)
