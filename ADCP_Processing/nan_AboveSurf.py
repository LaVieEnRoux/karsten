import numpy as np

def nan_AboveSurf(data, z, depth, threshold=0.95):
    '''
    Translation of the nan_AboveSurf.m program provided by Justine McMillan

    Places NaNs in all the values of data that are above the threshold
    multiplied by the surface height. Defaults to 95%.

    Inputs:
	data- Matrix of ADCP data (east or north velocities)
	z- ADCP bin depth
	depth- depth of water column at each timestep
	threshold- percentage of depth represented in output data
    '''

    z = np.asarray(z)
    bin_max = np.zeros(depth.size)

    # iterate through the timesteps
    for i in np.arange(depth.size):
	z_max = threshold * depth[i]
	bin_max[i] = np.argmin(abs(z - z_max))
	if z[bin_max[i]] > z_max:
	    bin_max[i] -= 1
	data[i, bin_max[i] + 1:z.size] = np.nan
