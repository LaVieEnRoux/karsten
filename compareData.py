import numpy as np
from tidalStats import TidalStats
from interpolate import interpol
from datetime import datetime, timedelta
import sys
sys.path.append('/array/home/116822s/github/UTide')
from utide import ut_reconstr

def loadDict(pts, time):
    '''
    Loads data into a dictionary for input into smooth and interpolate
    functions.
    '''
    out_d = {}
    out_d['pts'] = pts
    out_d['time'] = time

    return out_d

def dn2dt(datenum):
    '''
    Convert matlab datenum to python datetime.
    '''
    return datetime.fromordinal(int(datenum)) + timedelta(days=datenum%1) - \
           timedelta(days=366)

def compareUV(data):
    '''
    Does a comprehensive validation process between modeled and observed
    data on the following:
        Current speed
        Current direction
        Harmonic constituents (for height and speed)

    Outputs a list of important statistics for each variable, calculated
    using the TidalStats class
    '''
    # take data from input dictionary
    mod_time = data['mod_time']
    obs_time = data['obs_time']
    mod_u = data['mod_timeseries']['ua']
    mod_v = data['mod_timeseries']['va']
    obs_u = data['obs_timeseries']['u']
    obs_v = data['obs_timeseries']['v']
    mod_harm = data['speed_mod_harmonics']
    obs_harm = data['speed_obs_harmonics']
   
    # convert times to datetime
    mod_dt, obs_dt = [], []
    for i in mod_time:
	mod_dt.append(dn2dt(i))
    for j in obs_time:
	obs_dt.append(dn2dt(j))

    # put u v velocities into a useful format
    mod_spd = np.sqrt(mod_u**2 + mod_v**2)
    obs_spd = np.sqrt(obs_u**2 + obs_v**2)
    mod_dir = np.arctan(mod_v / mod_u)
    obs_dir = np.arctan(obs_v / obs_u)

    # check if the modeled data lines up with the observed data
    if (mod_time[-1] < obs_time[0] or obs_time[-1] < mod_time[0]):

	pred_uv = ut_reconstr(obs_time, mod_harm)
	pred_uv = np.asarray(pred_uv)

	# redo speed and direction and set interpolated variables
	mod_sp_int = np.sqrt(pred_uv[0]**2 + pred_uv[1]**2)
	mod_dr_int = np.arctan(pred_uv[0] / pred_uv[1])
	obs_sp_int = obs_spd
	obs_dr_int = obs_dir
	step_int = obs_dt[1] - obs_dt[0]
	start_int = obs_dt[0]

    else:
        # interpolate the data onto a common time step for each data type
#        mod_el_d = loadDict(mod_el, mod_step, mod_time[0], mod_time[-1])
#        obs_el_d = loadDict(obs_el, obs_step, obs_time[0], obs_time[-1])
#        (mod_el_int, obs_el_int, step_int, start_int) = \
#            interpol(mod_el_d, obs_el_d)

        mod_sp_d = loadDict(mod_spd, mod_dt)
        obs_sp_d = loadDict(obs_spd, obs_dt)
        (mod_sp_int, obs_sp_int, step_int, start_int) = \
            interpol(mod_sp_d, obs_sp_d)

        mod_dr_d = loadDict(mod_dir, mod_dt)
        obs_dr_d = loadDict(obs_dir, obs_dt)
        (mod_dr_int, obs_dr_int, step_int, start_int) = \
            interpol(mod_dr_d, obs_dr_d)

    # set up the comparison classes for each type of data
#    elev_stats = TidalStats(mod_el_int, obs_el_int, step_int, start_int)
    speed_stats = TidalStats(mod_sp_int, obs_sp_int, step_int, start_int)
    dir_stats = TidalStats(mod_dr_int, obs_dr_int, step_int, start_int)


    # obtain necessary statistics
#    elev_suite = elev_stats.getStats()
    speed_suite = speed_stats.getStats()
    dir_suite = dir_stats.getStats()

    # do some linear regression
#    elev_suite['r_squared'] = elev_stats.linReg()['r_2']
    speed_suite['r_squared'] = speed_stats.linReg()['r_2']
    dir_suite['r_squared'] = dir_stats.linReg()['r_2']

    # do statistic on harmonic constituents as well

    # output statistics in useful format
#    return (elev_suite, speed_suite, dir_suite)
    return (speed_suite, dir_suite)

def compareTG(data, site):
    '''
    Does a comprehensive comparison between tide gauge height data and
    modeled data, much like the above function.

    Input is a dictionary containing all necessary tide gauge and model data.
    Outputs a dictionary of useful statistics.
    '''
    # set up keys based on site input
    el_key = 'el{}'.format(site)
    dat_key = '{}_tg_data'.format(site)
    time_key = '{}_time'.format(site)
    obs_harm_key = '{}_tidegauge_harmonics'.format(site)
    mod_harm_key = '{}_mod_harmonics'.format(site)

    # load data
    mod_elev = data[el_key]
    obs_elev = data[dat_key]
    obs_datenums = data[time_key]
    mod_datenums = data['mod_time']
    
    # subtract mean from tidegauge stuff
    obs_elev = obs_elev - np.mean(obs_elev)

    # convert times and grab values
    obs_time, mod_time = [], [] 
    for i, v in enumerate(obs_datenums):
	obs_time.append(dn2dt(v))
    for j, w in enumerate(mod_datenums):
	mod_time.append(dn2dt(w))

    # interpolate timeseries onto a common timestep
    obs_dict = loadDict(obs_elev, obs_time)
    mod_dict = loadDict(mod_elev, mod_time)
    (obs_elev_int, mod_elev_int, step_int, start_int) = \
        interpol(mod_dict, obs_dict)

    # get validation statistics
    stats = TidalStats(obs_elev_int, mod_elev_int, step_int, start_int)
    elev_suite = stats.getStats()
    elev_suite['r_squared'] = stats.linReg()['r_2']

    return elev_suite
