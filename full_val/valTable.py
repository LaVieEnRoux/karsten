import cPickle as pickle
import numpy as np
import pandas as pd

# ALTERNATE VERSION FOR ANDY

def valTable(paths, vars):
    '''
    Takes validation data from the struct and saves it into a .csv file for
    each run.

    Takes a single argument, a dictionary whose keys are the run names, and
    values are the paths to the validation struct
    '''
    # iterate through the filenames
    for run in paths:

	# load in the struct
	in_f = open(paths[run], 'rb')
	struct = pickle.load(in_f)

	# initialize  lists
	val_dict = {}
	type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase = \
	[], [], [], [], [], [], [], [], [], [], [], []
	num_tg = 1

	# append to the lists the stats from each site for each variable
	for var in vars:
	    (type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2, phase) \
                = siteStats(struct, var, type, name, RMSE, CF, SD, POF,
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
    num_tg = 1

    for site in run:
 
        # check if it's a tidegauge site
        if ((site['type'] != 'TideGauge') and (variable != 'tg')):
            stats = site['{}_val'.format(variable)]
            type.append(variable)
            name.append(site['name'].split('/')[-1].split('.')[0])

        elif ((site['type'] == 'TideGauge') and (variable == 'tg')):
            stats = site['tg_val']
            type.append('elev')
            name.append(site['name'].split('/')[-1].split('.')[0])
            num_tg += 1

	# do nothing if a tidegauge is encountered but variable isn't tg
	else:
	    continue
    
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
