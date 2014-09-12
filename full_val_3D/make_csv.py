from loadValidation import loadValidation
from valTable import valTable
from validationStruct import main as makeStruct
import pandas as pd

'''
This code will take in a set of filenames for FVCOM, ADCP, and TG data, and
create a validation struct from them. It will then append 
'''

# set up paths to FVCOM files, ADCP files, and TideGauge files to create struct
fvFiles = ['/EcoII/EcoEII_server_data_tree/workspace/simulated/FVCOM/dngrid/july_2012_3D/output/']
adcpFiles = ['/EcoII/EcoEII_server_data_tree/code/jonCode/ADCP_Processing/GP-120726-BPd_avg_10min.mat']
tideFiles = ['/EcoII/EcoEII_server_data_tree/data/observed/GP/TideGauge/Westport_015892_20140325_1212_Z.mat',
             '/EcoII/EcoEII_server_data_tree/data/observed/DG/TideGauge/DigbyWharf_015893_20140115_2221_Z.mat']

# filenames for input validation structs
files = {}
files['july_2012_3D'] = '/EcoII/EcoEII_server_data_tree/workspace/simulated/' + \
                        'FVCOM/dngrid/july_2012_3D/output/validationStruct.p'

# options for vars: elev, speed, dir, tg, u, v, vel (ebb and flo to come soon)
vars = []
vars.append('elev')
vars.append('speed')
vars.append('dir')
vars.append('tg')

# create validation struct, and make .csv files from it
struct = makeStruct(fvFiles, adcpFiles, tideFiles, isStation=True)
print 'Struct created'
loadValidation(files)
print 'Validation loaded'
valTable(files, vars)
print 'CSV files created'
