import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt


class TidalHeightStats:
    '''
    An object representing a set of statistics on tidal heights used
    to determine the skill of a model in comparison to observed data.
    Standards are from NOAA's Standard Suite of Statistics.

    Instantiated with two arrays containing predicted and observed
    data, and the times corresponding to the data points. Begins by
    interpolating timesteps between the datasets so they line up.

    Functions are used to calculate statistics and to output
    visualizations and tables.
    '''
    def __init__(self, model_data, model_step, observed_data, observed_step):
        # find gcd between the time steps using euclidean algorithm
        a = model_step
        gcd = observed_step
        while a:
            a, gcd = a % gcd, a

        # calculate lcm from gcd, and solve: step * x = lcm
        lcm = model_step * observed_step / gcd
        mod_coef = lcm / model_step
        obs_coef = lcm / observed_step

        # slice data as necessary so times line up
        self.model = model_data[::mod_coef]
        self.observed = observed_data[::obs_coef]
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
        return np.sqrt(np.sum(self.error**2) / n)

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

    def linReg(self, alpha=0.05):
        '''
        Does linear regression on the model data vs. recorded data.

        Gives a 100(1-alpha)% confidence interval for the slope
        '''
        mod = self.model
        mod_mean = np.mean(mod)
        obs = self.observed
        obs_mean = np.mean(obs)
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
        intercept = obs_mean - slope * mod_mean
        sd_slope = np.sqrt(MSE / SSxx)
        r_squared = 1 - SSE / SSyy

        # calculate 100(1 - alpha)% CI for slope
        width = t.isf(0.5 * (1 - alpha), df) * sd_slope
        lower_bound = slope - width
        upper_bound = slope + width
        slope_CI = (lower_bound, upper_bound)

        # calculate 100(1 - alpha)% CI for intercept
        lower_intercept = obs_mean - lower_bound * mod_mean
        upper_intercept = obs_mean - upper_bound * mod_mean
        intercept_CI = (lower_intercept, upper_intercept)

        # estimate 100(1 - alpha)% CI for predictands
        predictands = slope * mod + intercept
        sd_resid = np.std(obs - predictands)
        y_CI_width = t.isf(0.5 * (1 - alpha), df) * sd_resid * \
            np.sqrt(1 - 1 / n)

        # return data in a dictionary
        data = {}
        data['slope'] = slope
        data['intercept'] = intercept
        data['r_2'] = r_squared
        data['slope_CI'] = slope_CI
        data['intercept_CI'] = intercept_CI
        data['pred_CI_width'] = y_CI_width
        data['conf_level'] = 100 * (1 - alpha)

        return data

    def crossVal(self, alpha=0.05):
        '''
        Performs leave-one-out cross validation on the linear regression.

        i.e. removes one datum from the set, redoes linreg on the training
        set, and uses the results to attempt to predict the missing datum.
        '''
        cross_error = np.zeroes(self.model.size)
        cross_pred = np.zeroes(self.model.size)
        model_orig = self.model
        obs_orig = self.observed
        time_orig = self.time

        # loop through each element, remove it
        for i in np.arange(self.model.size):
            train_mod = np.delete(model_orig, i)
            train_obs = np.delete(obs_orig, i)
            train_time = np.delete(time_orig, i)
            train_stats = TidalHeightStats(train_mod, train_obs, train_time)

            # redo the linear regression and get parameters
            param = train_stats.linReg(alpha)
            slope = param['slope']
            intercept = param['intercept']

            # predict the missing observed value and calculate error
            pred_obs = slope * model_orig[i] + intercept
            cross_pred[i] = pred_obs
            cross_error[i] = abs(pred_obs - obs_orig[i])

        # calculate PRESS and PRRMSE statistics for predicted data
        # (predicted residual sum of squares and predicted RMSE)
        PRESS = np.sum(cross_error**2)
        PRRMSE = np.sqrt(PRESS) / self.model.size

        # return data in a dictionary
        data = {}
        data['PRESS'] = PRESS
        data['PRRMSE'] = PRRMSE
        data['cross_pred'] = cross_pred

        return data

    def plotRegression(self, lr):
        '''
        Plots a visualization of the output from linear regression,
        including confidence intervals for predictands and slope.
        '''
        plt.scatter(self.model, self.observed, c='b', alpha=0.5)

        # plot regression line, with CI's
        mod_max = np.amax(self.model)
        upper_intercept = lr['intercept'] + lr['pred_CI_width']
        lower_intercept = lr['intercept'] - lr['pred_CI_width']

        plt.plot([0, mod_max], [lr['intercept'], mod_max * lr['slope'] +
                                lr['intercept']],
                 color='k', linestyle='-', linewidth=2)

        plt.plot([0, mod_max], [lr['intercept_CI'][0],
                                mod_max * lr['slope_CI'][0] +
                                lr['intercept_CI'][0]],
                 color='r', linestyle='--', linewidth=2)

        plt.plot([0, mod_max], [lr['intercept_CI'][1],
                                mod_max * lr['slope_CI'][1] +
                                lr['intercept_CI'][1]],
                 color='r', linestyle='--', linewidth=2)

        plt.plot([0, mod_max], [upper_intercept,
                                mod_max * lr['slope'] + upper_intercept],
                 color='g', linestyle='--', linewidth=2)

        plt.plot([0, mod_max], [lower_intercept,
                                mod_max * lr['slope'] + lower_intercept],
                 color='g', linestyle='--', linewidth=2)

        plt.xlabel('Modeled Data')
        plt.ylabel('Observed Data')
        plt.title('Modeled vs. Observed: Linear Fit')
        plt.show()

    def plotData(self, time, graph='time'):
        '''
        Provides a visualization of the data.

        Takes an option which determines the type of graph to be made.
        time: plots the model data against the observed data over time
        scatter : plots the model data vs. observed data
        '''
        if (graph == 'time'):
            plt.plot(time, self.model, label='Model Predictions')
            plt.plot(time, self.observed, colour='r',
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
