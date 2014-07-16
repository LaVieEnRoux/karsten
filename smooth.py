from datetime import timedelta
import numpy as np
import time


def smooth(data_1, data_2, time_step=timedelta(minutes=5)):
    '''
    Smooths a dataset by taking the average of all datapoints within
    a certain timestep to reduce noise. Lines up two datasets in the
    time domain, as well.

    Accepts two sets of data, each of which are dictionaries containing two
    values:
    time- array of datetimes corresponding to the timeseries
    pts- 1D numpy array containing the data

    Third optional argument sets the time between data points in the output
    data. Is a timedelta object, defaults to 5 minutes.
    '''
    dt_1 = data_1['time']
    dt_2 = data_2['time']

    # create POSIX timestamp array corresponding to each dataset
    times_1, times_2 = np.zeros(len(dt_1)), np.zeros(len(dt_2))
    for i in np.arange(times_1.size):
        times_1[i] = time.mktime(dt_1[i].timetuple())
    for i in np.arange(times_2.size):
        times_2[i] = time.mktime(dt_2[i].timetuple())

    # choose smoothing interval
    start = max(times_1[0], times_2[0])
    end = min(times_1[-1], times_2[-1])
    length = end - start

    # grab number of steps and timestamp for start time
    step_sec = time_step.total_seconds()
    steps = int(length / step_sec)

    # take averages at each step, create output data
    series_1, series_2 = np.zeros(steps), np.zeros(steps)
    for i in np.arange(steps):
        start_buf = start + step_sec * i
        end_buf = start + step_sec * (i + 1)

	buf_1 = np.where((times_1 >= start_buf) & (times_1 < end_buf))[0]
	buf_2 = np.where((times_2 >= start_buf) & (times_2 < end_buf))[0]	

	data_buf_1 = data_1['pts'][buf_1]
	data_buf_2 = data_2['pts'][buf_2]

	if (i % 500 == 0):
	    print 'Currently smoothing at step {} / {}'.format(i, steps)

        # calculate mean of data subsets (in the buffers)
	if (len(data_buf_1) != 0):
            series_1[i] = np.mean(data_buf_1)
	else:
	    series_1[i] = np.nan
	if (len(data_buf_2) != 0):
            series_2[i] = np.mean(data_buf_2)
	else:
	    series_2[i] = np.nan

	dt_start = max(dt_1[0], dt_2[0])

    return (series_1, series_2, time_step, dt_start)
