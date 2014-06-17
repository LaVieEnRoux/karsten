import numpy as np
import tidalStats
import interpolate
import smooth


def compareData(mod_el, obs_el, mod_u, obs_u, mod_v, obs_v, mod_harm,
                obs_harm):
    '''
    Does a comprehensive validation process between modeled and observed
    data on the following:
        Elevation
        Current speed
        Current direction
        Harmonic constituents

    Outputs a list of important statistics for each variable, calculated
    using the TidalStats class

    Assumes that each set of data is a dictionary with the following
    variables:
        data- array of data points
        time- array of datetimes corresponding to the data
    '''
