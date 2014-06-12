from scipy.interpolate import interp1d
import numpy as np
from datetime import timedelta
import time


def interpol(data_1, data_2, time_step=timedelta(minutes=10)):
    '''
    Interpolates between two datasets so their points line up in the time
    domain.

    Accepts two sets of data, each of which are dictionaries containing four
    values:
    start-  datetime object representing start of data
    end-    datetime object representing end of data
    step-   timedelta object representing time between data points
    pts-    1D numpy array containing the data

    Third optional argument sets the time between data points in the output
    data. Is a timedelta object, defaults to 10 minutes.
    '''

    # create POSIX timestamp array corresponding to each dataset
    times_1 = data_1['start'] + np.arange(data_1['pts'].size) * data_1['step']
    times_2 = data_2['start'] + np.arange(data_2['pts'].size) * data_2['step']
    for i in np.arange(times_1.size):
        times_1 = time.mktime(times_1[i].timetuple())
        times_2 = time.mktime(times_2[i].timetuple())

    # generate interpolation functions using linear interpolation
    f1 = interp1d(times_1, data_1['data'])
    f2 = interp1d(times_2, data_2['data'])

    # choose interval on which to interpolate
    start = max(data_1['start'], data_2['start'])
    end = min(data_2['end'], data_2['end'])
    length = end - start

    # determine number of steps in the interpolation interval
    steps = 0
    while length > time_step:
        length -= time_step
        steps += 1

    # create POSIX timestamp array for new data and perform interpolation
    output_times = start + np.arange(steps) * time_step
    for i in np.arange(steps):
        output_times = time.mktime(output_times[i].timetuple())

    series_1 = f1(output_times)
    series_2 = f2(output_times)

    return (series_1, series_2)
