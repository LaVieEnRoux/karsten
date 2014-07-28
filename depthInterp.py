import numpy as np
from scipy.interpolate import interp1d

'''
ASSUMPTIONS:
first dimension of matrices identify the timestep, second the depth
column vectors are organized from bottom to top
i.e. data[3] is the column at the third timestep
     data[3][10] is the tenth layer from the bottom at the third timestep
ADCP bins are the depths of each ADCP layer
ADCP bin width is constant
ADCP bin number is constant
The top ADCP value of any column is no greater than 95% of the total depth
'''

ADCP_TOP_SURF = 0.95
NUM_BINS = 20
BIN_WIDTH = 2

def depthToSigma(obs_data, obs_depth, siglay):
    '''
    Performs linear interpolation on 3D ADCP data to change it into a sigma
    layer format, similar to an FVCOM run.

    Outputs a 2D numpy array representing the ADCP data in sigma layer
    format.
    '''

    sig_obs = np.zeros(obs_data.shape[0], siglay.size)

    # loop through columns/steps
    for i, column in enumerate(obs_data):

	# map old depths to between 0 and 1, make interpolation function
	col_nonan = column[np.where(~np.isnan(column))[0]]
	old_depths = np.arange(0, obs_depth[i] * ADCP_TOP_SURF, 
		     1. / col_nonan.size)
	mapped_depths = old_depths / obs_depth[i]
	f_obs = interp1d(col_nonan, mapped_depths)

	# perform interpolation
	sig_obs[i] = f_obs(siglay)

    return sig_obs

def sigmaToDepth(mod_data, mod_depth, siglay):
    '''
    Performs linear interpolation on 3D FVCOM output to change it into the
    same format as ADCP output (i.e. constant depths, NaNs above surface)

    Outputs a 2D numpy array representing the FVCOM matrix in ADCP format.
    '''

    bin_mod = np.zeros(mod_data.shape[0], NUM_BINS)

    # loop through columns/steps
    for i, column in enumerate(mod_data):
	
	# create interpolation function
	f_mod = interp1d(column, siglay)
	depth = mod_depth[i]

	# loop through bins
	for j in np.arange(NUM_BINS):

	    # check if location is above ADCP_TOP_SURF
	    loc = float(BIN_WIDTH * j) / float(depth)
	    if (loc <= ADCP_TOP_SURF):
		bin_mod[i][j] = f_mod(loc)
	    else:
		bin_mod[i][j] = np.nan

    return bin_mod

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

    new_mod = np.zeros(mod_data.shape[0])
    new_obs = np.zeros(obs_data.shape[0])

    # loop over mod_data columns
    for i, step in enumerate(mod_data):

        # create interpolation function
	f_mod = interp1d(step, siglay)

	# find location of specified depth and perform interpolation
	location = mod_depth[i] - depth
	sig_loc = float(location) / float(mod_depth[i])
	new_mod[i] = f_mod(sig_loc)

    # loop over obs_data columns
    for ii, column in enumerate(obs_data):

	# create interpolation function
	col_nonan = column[np.where(~np.isnan(column))[0]]
	top_depth = ADCP_TOP_SURF * obs_depth[ii]
	index = np.arange(0, top_depth, 1. / col_nonan.size)
	f_obs = interp1d(column, index)

	# find location of specified depth and perform interpolation
	location = obs_depth[ii] - depth
	new_obs[i] = f_obs(location)

    return (new_mod, new_obs)
