from datetime import timedelta
import numpy as np
import time


def smooth(data_1, data_2, time_step=timedelta(minutes=10)):
    '''
    Smooths a dataset by taking the average of all datapoints within
    a certain timestep to reduce noise. Lines up two datasets in the
    time domain, as well.

    Accepts two sets of data, each of which are dictionaries containing four
    values:
    start- datetime object representing start of data
    end- datetime object representing end of data
    step- timedelta object representing time between data points
    pts- 1D numpy array containing the data

    Third optional argument sets the time between data points in the output
    data. Is a timedelta object, defaults to 10 minutes.
    '''

    print data_1['start']
    print data_1['end']
    print data_1['step']
    print data_2['start']
    print data_2['end']
    print data_2['step']

    # create POSIX timestamp array corresponding to each dataset
    times_1 = data_1['start'] + np.arange(data_1['pts'].size) * data_1['step']
    print times_1[:20]
    times_2 = data_2['start'] + np.arange(data_2['pts'].size) * data_2['step']
    for i in np.arange(times_1.size):
        times_1[i] = time.mktime(times_1[i].timetuple())
    for i in np.arange(times_2.size):
        times_2[i] = time.mktime(times_2[i].timetuple())

    print times_1[:20]

    # get number of seconds in time_step, and smoothing interval
    step_sec = time_step.total_seconds()
    start = max(data_1['start'], data_2['start'])
    end = min(data_2['end'], data_2['end'])
    length = (end - start).total_seconds()

    # grab number of steps and timestamp for start time
    steps = int(length / step_sec)
    print steps
    start_POS = time.mktime(start.timetuple())

    # take averages at each step, create output data
    series_1, series_2 = np.zeros(steps), np.zeros(steps)
    for i in np.arange(steps):
        start_buf = start_POS + step_sec * i
        end_buf = start_POS + step_sec * (i + 1)
        buf_1 = times_1[(times_1 >= start_buf) &
                        (times_1 < end_buf)]
        buf_2 = times_2[(times_2 >= start_buf) &
                        (times_2 < end_buf)]

        # iterate through buffers to find corresponding data values
        data_buf_1, data_buf_2 = [], []
        for j, k in enumerate(buf_1):
            index = np.where(times_1 == k)[0][0]
            data_buf_1.append(data_1['pts'][index])
        for j, k in enumerate(buf_2):
            index = np.where(times_2 == k)[0][0]
            data_buf_2.append(data_2['pts'][index])

        # calculate mean of data subsets (in the buffers)
        series_1[i] = np.mean(data_buf_1)
        series_2[i] = np.mean(data_buf_2)

    return (series_1, series_2, time_step, start)
