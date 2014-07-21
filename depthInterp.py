import numpy as np
from scipy.interpolate import interp1d

def depthToSigma():

def sigmaToDepth():

def depthFromSurf(mod_data, mod_depth, siglay, 
		  obs_data, obs_depths, depth=5):
    '''
    I will write a good comment later.
    '''

    # loop over mod_data columns
    for i, step in enumerate(mod_data):

        # create interpolation function
	f_mod = interp1d(step, siglay) # making some assumptions about siglay here

	# find location of specified depth
	location = mod_depth[i] - depth
	sig_loc = float(location) / float(mod_depth[i])

	# perform interpolation to get new data
	new_data = f_mod(sig_loc)

    # loop over obs_data columns
    for column in obs_data:

	# remove nans at the top
	col_nonan = column[np.where(~np.isnan(column))[0]]

	# create interpolation function
	index = np.arange(col_nonan.size)
	f_obs = interp1d(column, index)

	# find location of specified depth

	# perform interpolation to get new data
