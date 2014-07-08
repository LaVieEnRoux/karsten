import scipy.io
import numpy as np

def loadDrift(obs_file):
    '''
    Loads in drifter data from an observed drifter.

    Takes the filepath of the drifter data as an argument.
    '''

    # load in observed data and grabs lat/lon
    obs_struct = scipy.io.loadmat(obs_file)
    obs_time = obs_struct['gps_observation'][0][0][0]
    obs_lat = obs_struct['gps_observation'][0][0][1]
    obs_lon = obs_struct['gps_observation'][0][0][2]

    return (obs_time, obs_lat, obs_lon)


