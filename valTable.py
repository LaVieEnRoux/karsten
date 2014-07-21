import cPickle as pickle
import numpy as np
import pandas as pd

def valTable(filename):
    '''
    Takes validation data from the struct and saves it into a .csv file for
    each run.

    Takes a single argument, the filename of the struct.
    '''
    # load in the struct
    in_f = open(filename, 'rb')
    struct = pickle.load(in_f)

    # iterate through the runs
    for run in struct:

	# initialize  lists
	val_dict = {}
	type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase = \
	[], [], [], [], [], [], [], [], [], [], [], []
	num_tg = 1

	# append to the lists the stats from each site for each variable
	(type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
	    = siteStats(struct[run], 'elev', type, name, RMSE, CF, SD, POF,
			NOF, MDPO, MDNO, skill, r2, phase)
        (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
            = siteStats(struct[run], 'speed', type, name, RMSE, CF, SD, POF,
                        NOF, MDPO, MDNO, skill, r2, phase)
        (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
            = siteStats(struct[run], 'dir', type, name, RMSE, CF, SD, POF,
                        NOF, MDPO, MDNO, skill, r2, phase)
        (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
            = siteStats(struct[run], 'u', type, name, RMSE, CF, SD, POF,
                        NOF, MDPO, MDNO, skill, r2, phase)
        (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
            = siteStats(struct[run], 'v', type, name, RMSE, CF, SD, POF,
                        NOF, MDPO, MDNO, skill, r2, phase)
        (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
            = siteStats(struct[run], 'vel', type, name, RMSE, CF, SD, POF,
                        NOF, MDPO, MDNO, skill, r2, phase)

	# put stats into dict and create dataframe
	val_dict = {'Type':type, 'RMSE':RMSE, 'CF':CF, 'SD':SD, 'POF':POF,
		    'NOF':NOF, 'MDPO':MDPO, 'MDNO':MDNO,  'skill':skill,
		    'r2':r2, 'phase':phase}

	table = pd.DataFrame(data=val_dict, index=name,
			     columns=val_dict.keys())

	# export as .csv file
	out_file = 'valTables/{}_val.csv'.format(run)
	table.to_csv(out_file)

def siteStats(run, variable, type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, 
	      skill, r2, phase):
    '''
    Iterates through the sites for a particular run, and grabs the individual
    statistics for each site.

    Takes in the run (an array of dictionaries) and the type of the run (a
    string). Also takes in the list representing each statistic.
    '''
    for site in run:
    
        # check if it's a tidegauge site
        if ('obs_time' in site.keys()):
            stats = site['{}_val'.format(variable)]
            type.append(variable)
            name.append(site['name'])
    
        else:
            stats = site['dg_elev_val']
            type.append('Elevation')
            name.append('TG{}'.format(num_tg))
            num_tg += 1
    
        RMSE.append(stats['RMSE'])
        CF.append(stats['CF'])
        SD.append(stats['SD'])
        POF.append(stats['POF'])
        NOF.append(stats['NOF'])
        MDPO.append(stats['MDPO'])
        MDNO.append(stats['MDNO'])
        skill.append(stats['skill'])
        r2.append(stats['r_squared'])
        phase.append(stats['phase'])

    return (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase)
