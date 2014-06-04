from __future__ import division
import datetime
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from ut_solv import *
from ut_reconstr import *
from mpl_toolkits.basemap import Basemap


def datetime2matlabdn(dt):
    '''
    Converts a datetime string to a matlab compatible datenum
    '''
    mdn = dt + timedelta(days=366)
    frac = (dt-datetime(dt.year, dt.month, dt.day, 0, 0, 0)).seconds / \
        (24.0 * 60.0 * 60.0)
    return mdn.toordinal() + frac


def load_coef(filename):
    '''
    Loads harmonic constituents, longitude, and latitude from a .nc file.
    Puts harmonic data into a struct.
    '''
    data = nc.Dataset(filename, 'r')
    coef.a = data.variables['coef.a'][:]
    coef.g = data.variables['coef.g'][:]
    # load all the other coef vars- INCOMPLETE
    lon = data.variables['lon'][:]
    lat = data.variables['lat'][:]

    # load coef vars into coef struct- INCOMPLETE

    return (coef, lon, lat)


def get_heights(coef, lon, lat, start_date, time_span='day'):
    '''
    Creates an array of times, then returns tidal height data for those times
    over the entire grid using ut_reconstr().

    Takes an option for spacing of times. They can span a day, half a day,
    or an hour.

    Outputs data in the form of a matrix containing a time series for each
    gridpoint.
    '''

    # change start_date into a datetime format, then into a datenum
    format = '%Y-%m-%d %H:%M:%S.%f'
    date = datetime.datetime.strptime(start_time, format)
    date = datetime2matlabdn(date)

    # set up array of timesteps based on defined span
    if (time_span == 'day'):
        t = np.arange(date, date + 1, 24, dtype='float')
    if (time_span == 'half_day'):
        t = np.arange(date, date + 0.5, 12, dtype='float')
    if (time_span == 'hour'):
        t = np.arange(date, date + 1/24, 60, dtype='float')

    # input data into ut_reconstr point by point, load into matrix
    time_series = np.zeros(lon.size, t.size)
    for i in np.arange(lon.size):
        time_series[i] = ut_reconstr(t[i], coef[i])

    return time_series


def draw_tides(time_series, lat, lon, bath):
    '''
    Plot tidal heights on a map of Nova Scotia using a colormesh.

    Currently shows a plot, but eventually will simply return an
    image file.
    '''
    plt.figure()

    # set up the basemap based on lat/lon values
    m = Basemap(projection='miller', llcrnrlon=lon.min(),
                urcrnrlon=lon.max(), llcrnrlat=lat.min(),
                urcrnrlat=lat.max(), resolution='h')

    # set dry spots to extraneous value -INCOMPLETE

    # convert lat/lon to x/y projections
    x, y = m(lon, lat)

    # let there be colour
    colour = m.pcolormesh(x, y, time_series, shading='flat',
                          cmap=plt.cm.jet)

    # add lines -INCOMPLETE
    colorbar(colour)
    plt.title('Fundy Bay Tidal Heights')
    plt.show()
