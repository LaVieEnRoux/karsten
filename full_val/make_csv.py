from loadValidation import loadValidation
from valTable import valTable
import pandas as pd

# ALTERNATE VERSION FOR ANDY

'''
This version of make_csv.py runs with a set of structs instead of one
'''

# paths for appended structs
paths = {}
paths['0.0015'] = '0.0015_val_struct.p'
paths['0.0020'] = '0.0020_val_struct.p'
paths['0.0025'] = '0.0025_val_struct.p'
paths['0.002848'] = '0.002848_val_struct.p'
paths['0.0030'] = '0.0030_val_struct.p'

# filenames for input validation structs
files = {}
files['0.0015'] = '/EcoII/EcoEII_server_data_tree/workspace/simulated/' + \
                  'FVCOM/dngrid/calibration/bottom_roughness/2D/0.0015/output/validationStruct.p'
files['0.0020'] = '/EcoII/EcoEII_server_data_tree/workspace/simulated/' + \
                  'FVCOM/dngrid/calibration/bottom_roughness/2D/0.0020/output/validationStruct.p'
files['0.0025'] = '/EcoII/EcoEII_server_data_tree/workspace/simulated/' + \
                  'FVCOM/dngrid/calibration/bottom_roughness/2D/0.0025/output/validationStruct.p'
files['0.002848'] = '/EcoII/EcoEII_server_data_tree/workspace/simulated/' + \
                    'FVCOM/dngrid/calibration/bottom_roughness/2D/0.002848/output/validationStruct.p'
files['0.0030'] = '/EcoII/EcoEII_server_data_tree/workspace/simulated/' + \
                  'FVCOM/dngrid/calibration/bottom_roughness/2D/0.0030/output/validationStruct.p'

# options for vars: elev, speed, dir, tg, u, v, vel (ebb and flo to come soon)
vars = []
vars.append('elev')
vars.append('speed')
vars.append('dir')
vars.append('tg')

# create validation struct, and make .csv files from it
loadValidation(files)
valTable(paths, vars)
