import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt
import pandas as pd


class TidalHeightStats:
    '''
    An object representing a set of statistics on tidal heights used
    to determine the skill of a model in comparison to observed data.
    Standards are from NOAA's Standard Suite of Statistics.

    Instantiated with two arrays containing predicted and observed
    data, and the times corresponding to the data points. Times are in
    datetime format.

    Functions are used to calculate statistics and to output
    visualizations and tables.
    '''
    def __init__(self, model_data, observed_data, data_times):
        self.model = model_data
        self.observed = observed_data
        self.time = data_times
        self.error = model_data - observed_data

    # establish limits as defined by NOAA standard
    CF_MIN = 90
    POF_MAX = 1
    NOF_MAX = 1
    WOF_MAX = 0.5
    MDO_MAX = 1440
    ERROR_BOUND = 0.015

    def getRMSE(self):
        '''
        Returns the root mean squared error of the data.
        '''
        n = self.error.size
        return np.sqrt((self.error**2) / n)

    def getSD(self):
        '''
        Returns the standard deviation of the error.
        '''
        return np.sqrt((abs(self.error - self.error.mean())**2).mean)

    def getCF(self):
        '''
        Returns the central frequency of the data, i.e. the fraction of
        errors that lie within the defined limit.
        '''
        central_err = np.where(self.error < self.ERROR_BOUND)
        central_num = central_err[0].size
        total = self.error.size

        return (central_num / total) * 100

    def getPOF(self):
        '''
        Returns the positive outlier frequency of the data, i.e. the
        fraction of errors that lie above the defined limit.
        '''
        upper_err = np.where(self.error > 2 * self.ERROR_BOUND)
        upper_num = upper_err[0].size
        total = self.error.size

        return (upper_num / total) * 100

    def getNOF(self):
        '''
        Returns the negative outlier frequency of the data, i.e. the
        fraction of errors that lie below the defined limit.
        '''
        lower_err = np.where(self.error < -2 * self.ERROR_BOUND)
        lower_num = lower_err[0].size
        total = self.error.size

        return (lower_num / total) * 100

    def getMDPO(self, timestep):
        '''
        Returns the maximum duration of positive outliers, i.e. the
        longest amount of time across the data where the model data
        exceeds the observed data by a specified limit.

        Takes one parameter: the number of minutes between consecutive
        data points.
        '''
        max_duration = 0
        current_duration = 0
        for i in np.arange(self.error.size):
            if (self.error > self.ERROR_BOUND):
                current_duration += timestep
            else:
                if (current_duration > max_duration):
                    max_duration = current_duration
                current_duration = 0

        return max_duration

    def getMDNO(self, timestep):
        '''
        Returns the maximum duration of negative outliers, i.e. the
        longest amount of time across the data where the observed
        data exceeds the model data by a specified limit.

        Takes one parameter: the number of minutes between consecutive
        data points.
        '''
        max_duration = 0
        current_duration = 0
        for i in np.arange(self.error.size):
            if (self.error < -self.ERROR_BOUND):
                current_duration += timestep
            else:
                if (current_duration > max_duration):
                    max_duration = current_duration
                current_duration = 0

        return max_duration

    def getStats(self, timestep):
        '''
        Returns each of the statistics in a dictionary.
        '''
        stats = {}
        stats['RMSE'] = self.getRMSE()
        stats['CF'] = self.getCF()
        stats['SD'] = self.getSD()
        stats['POF'] = self.getPOF()
        stats['NOF'] = self.getNOF()
        stats['MDPO'] = self.getMDPO(timestep)
        stats['MDNO'] = self.getMDNO(timestep)

        return stats

    def linReg(self, alpha):
        '''
        Does linear regression on the model data vs. recorded data.

        Gives a 100(1-alpha)% confidence interval for the slope
        '''
        mod = self.model
        obs = self.observed
        n = mod.size
        df = n - 2

        # calculate square sums
        SSxx = np.sum(mod**2) - np.sum(mod)**2 / n
        SSyy = np.sum(obs**2) - np.sum(obs)**2 / n
        SSxy = np.sum(mod * obs) - np.sum(mod) * np.sum(obs) / n
        SSE = SSyy - SSxy**2 / SSxx
        MSE = SSE / df

        # estimate parameters
        slope = SSxy / SSxx
        intercept = np.mean(obs) - slope * np.mean(mod)
        sd_slope = np.sqrt(MSE / SSxx)
        r_squared = 1 - SSE / SSyy

        # calculate 100(1 - alpha)% CI for slope
        width = t.isf(0.5 * (1 - alpha), df) * sd_slope
        lower_bound = slope - width
        upper_bound = slope + width

        # return data in a dictionary
        data = {}
        data['slope'] = slope
        data['intercept'] = intercept
        data['r_2'] = r_squared
        data['CI_lower'] = lower_bound
        data['CI_upper'] = upper_bound
        data['conf_level'] = 100 * (1 - alpha)

        return data

    def plotData(self, graph='time'):
        '''
        Provides a visualization of the data.

        Takes an option which determines the type of graph to be made.
        time: plots the model data against the observed data over time
        scatter : plots the model data vs. observed data
        '''
        if (graph == 'time'):
            plt.plot(self.time, self.model, label='Model Predictions')
            plt.plot(self.time, self.observed, colour='r',
                     label='Observed Data')
            plt.xlabel('Time')
            plt.ylabel('Tidal Height')
            plt.title('Tidal Heights: Predicted and Observed')
            plt.show()

        if (graph == 'scatter'):
            plt.scatter(self.model, self.observed, c='b', alpha=0.5)
            plt.xlabel('Predicted Height')
            plt.ylabel('Observed Height')
            plt.title('Tidal Heights')
            plt.show()
