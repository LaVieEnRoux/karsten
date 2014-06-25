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
	type, name, RMSE, CF, SD, POF, NOF, MDPO, MDNO, skill, r2 = \
	[], [], [], [], [], [], [], [], [], [], []
	num_tg = 1

	# iterate through sites and get validation stats
	for site in struct[run]:
	    
	    # check if it's a tidegauge site
	    if ('obs_time' in site.keys()):
		stats = site['speed_val']
		type.append('Speed')
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

	# put stats into dict and create dataframe
	val_dict = {'Type':type, 'RMSE':RMSE, 'CF':CF, 'SD':SD, 'POF':POF, 
		    'NOF':NOF, 'MDPO':MDPO, 'MDNO':MDNO,  'skill':skill, 
		    'r2':r2}
	
	table = pd.DataFrame(data=val_dict, index=name,
			     columns=val_dict.keys())

	# export as .csv file
	path_base = '/array/home/rkarsten/common_tidal_files/python/jonCode/'
	out_file = path_base + '{}_val.csv'.format(run)
	table.to_csv(out_file)

file = '/array/home/rkarsten/common_tidal_files/python/jonCode/val_struct.pkl'
valTable(file)
