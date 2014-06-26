import numpy as np
from scipy.stats import t
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import time

class TidalStats:
    '''
    An object representing a set of statistics on tidal heights used
    to determine the skill of a model in comparison to observed data.
    Standards are from NOAA's Standard Suite of Statistics.

    Instantiated with two arrays containing predicted and observed
    data which have already been interpolated so they line up, the
    time step between points, and the start time of the data.

    To remove NaNs in observed data, linear interpolation is performed to
    fill gaps.

    Functions are used to calculate statistics and to output
    visualizations and tables.
    '''
    def __init__(self, model_data, observed_data, time_step, start_time):
	self.model = np.asarray(model_data)
	self.model = self.model.astype(np.float64)
	self.observed = np.asarray(observed_data)
	self.observed = self.observed.astype(np.float64)

        # set up array of datetimes corresponding to the data (and timestamps)
        self.times = start_time + np.arange(model_data.size) * time_step
        self.step = time_step
	timestamps = np.zeros(len(self.times))
	for j, jj in enumerate(self.times):
	    timestamps[j] = time.mktime(jj.timetuple())

	# use linear interpolation to eliminate any NaNs in the observed data
	obs_nonan = self.observed[np.where(~np.isnan(self.observed))[0]]
	time_nonan = timestamps[np.where(~np.isnan(self.observed))[0]]
	func = interp1d(time_nonan, obs_nonan)
	self.observed = func(timestamps)

	self.error = self.observed - self.model

    # establish limits as defined by NOAA standard
    MDO_MAX = 1440
    ERROR_BOUND = 0.5

    def getRMSE(self):
        '''
        Returns the root mean squared error of the data.
        '''
        return np.sqrt(np.mean(self.error**2))

    def getSD(self):
        '''
        Returns the standard deviation of the error.
        '''
        return np.sqrt(np.mean(abs(self.error - np.mean(self.error)**2)))

    def getCF(self):
        '''
        Returns the central frequency of the data, i.e. the fraction of
        errors that lie within the defined limit.
        '''
        central_err = [i for i in self.error if abs(i) < self.ERROR_BOUND]
        central_num = len(central_err)
        total = self.error.size

        return (float(central_num) / float(total)) * 100

    def getPOF(self):
        '''
        Returns the positive outlier frequency of the data, i.e. the
        fraction of errors that lie above the defined limit.
        '''
        upper_err = [i for i in self.error if i > 2 * self.ERROR_BOUND]
        upper_num = len(upper_err)
        total = self.error.size

        return (float(upper_num) / float(total)) * 100

    def getNOF(self):
        '''
        Returns the negative outlier frequency of the data, i.e. the
        fraction of errors that lie below the defined limit.
        '''
        lower_err = [i for i in self.error if i < -2 * self.ERROR_BOUND]
        lower_num = len(lower_err)
        total = self.error.size

        return (float(lower_num) / float(total)) * 100

    def getMDPO(self):
        '''
        Returns the maximum duration of positive outliers, i.e. the
        longest amount of time across the data where the model data
        exceeds the observed data by a specified limit.

        Takes one parameter: the number of minutes between consecutive
        data points.
        '''
        timestep = self.step.seconds / 60

        max_duration = 0
        current_duration = 0
        for i in np.arange(self.error.size):
            if (self.error[i] > self.ERROR_BOUND):
                current_duration += timestep
            else:
                if (current_duration > max_duration):
                    max_duration = current_duration
                current_duration = 0

        return max_duration

    def getMDNO(self):
        '''
        Returns the maximum duration of negative outliers, i.e. the
        longest amount of time across the data where the observed
        data exceeds the model data by a specified limit.

        Takes one parameter: the number of minutes between consecutive
        data points.
        '''
        timestep = self.step.seconds / 60

        max_duration = 0
        current_duration = 0
        for i in np.arange(self.error.size):
            if (self.error[i] < -self.ERROR_BOUND):
                current_duration += timestep
            else:
                if (current_duration > max_duration):
                    max_duration = current_duration
                current_duration = 0

        return max_duration

    def getWillmott(self):
        '''
        Returns the Willmott skill statistic.
        '''

        # start by calculating MSE
        MSE = np.mean(self.error**2)

        # now calculate the rest of it
        obs_mean = np.mean(self.observed)
        skill = 1 - MSE / np.mean((abs(self.model - obs_mean) +
                                   abs(self.observed - obs_mean))**2)

        return skill

    def getStats(self):
        '''
        Returns each of the statistics in a dictionary.
        '''

        stats = {}
        stats['RMSE'] = self.getRMSE()
        stats['CF'] = self.getCF()
        stats['SD'] = self.getSD()
        stats['POF'] = self.getPOF()
        stats['NOF'] = self.getNOF()
        stats['MDPO'] = self.getMDPO()
        stats['MDNO'] = self.getMDNO()
        stats['skill'] = self.getWillmott()

        return stats

    def linReg(self, alpha=0.05):
        '''
        Does linear regression on the model data vs. recorded data.

        Gives a 100(1-alpha)% confidence interval for the slope
        '''
	# get rid of those friggin NaNs
	obs = self.observed
	mod = self.model
        obs_mean = np.mean(obs)
	mod_mean = np.mean(mod)
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
        width = t.isf(0.5 * alpha, df) * sd_slope
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
        y_CI_width = t.isf(0.5 * alpha, df) * sd_resid * \
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
            train_stats = TidalStats(train_mod, train_obs, train_time)

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
        plt.scatter(self.model, self.observed, c='b', marker='+', alpha=0.5)

        # plot regression line
        mod_max = np.amax(self.model)
	mod_min = np.amin(self.model)
        upper_intercept = lr['intercept'] + lr['pred_CI_width']
        lower_intercept = lr['intercept'] - lr['pred_CI_width']
        plt.plot([mod_min, mod_max], [mod_min * lr['slope'] + lr['intercept'], 
				      mod_max * lr['slope'] + lr['intercept']],
                 color='k', linestyle='-', linewidth=2)

        # plot CI's for slope
        plt.plot([mod_min, mod_max], 
		 [mod_min * lr['slope_CI'][0] + lr['intercept_CI'][0], 
		  mod_max * lr['slope_CI'][0] + lr['intercept_CI'][0]],
                 color='r', linestyle='--', linewidth=2)
        plt.plot([mod_min, mod_max], 
		 [mod_min * lr['slope_CI'][1] + lr['intercept_CI'][1],
                  mod_max * lr['slope_CI'][1] + lr['intercept_CI'][1]],
                 color='r', linestyle='--', linewidth=2)

        # plot CI's for predictands
        plt.plot([mod_min, mod_max], 
		 [mod_min * lr['slope'] + upper_intercept,
                  mod_max * lr['slope'] + upper_intercept],
                 color='g', linestyle='--', linewidth=2)
        plt.plot([mod_min, mod_max], 
		 [mod_min * lr['slope'] + lower_intercept,
                  mod_max * lr['slope'] + lower_intercept],
                 color='g', linestyle='--', linewidth=2)

	# plot y=x for comparison
	plt.plot([mod_min, mod_min], [mod_max, mod_max], color='k', 
		 linewidth=1)

        plt.xlabel('Modeled Data')
        plt.ylabel('Observed Data')
        plt.title('Modeled vs. Observed: Linear Fit')

	r_string = 'R Squared: {}'.format(lr['r_2'])
	plt.text(mod_max - 2, 0, r_string)
	plt.show()

	#plt.savefig('/array/home/rkarsten/common_tidal_files/python/jonCode/regressionPlot.png')

    def plotData(self, graph='time'):
        '''
        Provides a visualization of the data.

        Takes an option which determines the type of graph to be made.
        time: plots the model data against the observed data over time
        scatter : plots the model data vs. observed data
        '''
        if (graph == 'time'):
            plt.plot(self.times, self.model, label='Model Predictions')
            plt.plot(self.times, self.observed, color='r',
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
