import numpy as np
from tidalStats import TidalStats
import interpolate
import smooth

def loadDict(pts, step, start, end):
    '''
    Loads data into a dictionary for input into smooth and interpolate
    functions.
    '''
    out_d = {}
    out_d['pts'] = pts
    out_d['step'] = step
    out_d['start'] = start
    out_d['end'] = end

    return out_d

def compareData(mod_el, obs_el, mod_u, obs_u, mod_v, obs_v, mod_harm,
                obs_harm, mod_time, obs_time):
    '''
    Does a comprehensive validation process between modeled and observed
    data on the following:
        Elevation
        Current speed
        Current direction
        Harmonic constituents

    Outputs a list of important statistics for each variable, calculated
    using the TidalStats class
    '''

    # grab some important values
    mod_step = mod_time[1] - mod_time[0]
    obs_step = obs_time[1] - obs_time[0]

    # put u v velocities into a useful format
    mod_spd = np.sqrt(mod_u**2 + mod_v**2)
    obs_spd = np.sqrt(obs_u**2 + obs_v**2)
    mod_dir = np.arctan(mod_v / mod_u)
    obs_dir = np.arctan(obs_v / obs_u)

    # interpolate the data onto a common time step for each data type
    m d_el_d = loadDict(mod_el, mod_step, mod_time[0], mod_time[-1])
    obs_el_d = loadDict(obs_el, obs_step, obs_time[0], obs_time[-1])
    (mod_el_int, obs_el_int, step_int, start_int) = \
        interpolate.interpol(mod_el_d, obs_el_d)

    mod_sp_d = loadDict(mod_spd, mod_step, mod_time[0], mod_time[-1])
    obs_sp_d = loadDict(obs_spd, obs_step, obs_time[0], obs_time[-1])
    (mod_sp_int, obs_sp_int, step_int, start_int) = \
        interpolate.interpol(mod_sp_d, obs_sp_d)

    mod_dr_d = loadDict(mod_dir, mod_step, mod_time[0], mod_time[-1])
    obs_dr_d = loadDict(obs_dir, obs_step, obs_time[0], obs_time[-1])
    (mod_dr_int, obs_dr_int, step_int, start_int) = \
        interpolate.interpol(mod_dr_d, obs_dr_d)

    # set up the comparison classes for each type of data
    elev_stats = TidalStats(mod_el_int, obs_el_int, step_int, start_int)
    speed_stats = TidalStats(mod_sp_int, obs_sp_int, step_int, start_int)
    dir_stats = TidalStats(mod_dr_int, obs_dr_int, step_int, start_int)

    # obtain necessary statistics
    elev_suite = elev_stats.getStats()
    speed_suite = speed_stats.getStats()
    dir_suite = dir_stats.getStats()

    # do some linear regression
    elev_suite['r_squared'] = elev_stats.linReg()['r_2']
    speed_suite['r_squared'] = speed_stats.linReg()['r_2']
    dir_suite['r_squared'] = dir_stats.linReg()['r_2']

    # do statistic on harmonic constituents as well

    # output statistics in useful format
