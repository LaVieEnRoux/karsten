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

    print data_1['start'], data_1['end']
    print data_2['start'], data_2['end']

    # create POSIX timestamp array corresponding to each dataset
    times_1 = data_1['start'] + np.arange(data_1['pts'].size) * data_1['step']
    times_2 = data_2['start'] + np.arange(data_2['pts'].size) * data_2['step']
    for i in np.arange(times_1.size):
        times_1[i] = time.mktime(times_1[i].timetuple())
    for i in np.arange(times_2.size):
        times_2[i] = time.mktime(times_2[i].timetuple())

    # generate interpolation functions using linear interpolation
    f1 = interp1d(times_1, data_1['pts'])

    print times_2.shape, data_2['pts']
    f2 = interp1d(times_2, data_2['pts'])

    # choose interval on which to interpolate
    start = max(data_1['start'], data_2['start'])
    end = min(data_1['end'], data_2['end'])
    length = end - start

    # determine number of steps in the interpolation interval
    length_sec = length.total_seconds()
    step_sec = time_step.total_seconds()
    steps = int(length_sec / step_sec)

    # create POSIX timestamp array for new data and perform interpolation
    output_times = start + np.arange(steps) * time_step
    for i in np.arange(steps):
        output_times[i] = time.mktime(output_times[i].timetuple())

    series_1 = f1(output_times)
    series_2 = f2(output_times)

    return (series_1, series_2, time_step, start)
