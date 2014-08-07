from loadValidation import loadValidation
from valTable import valTable
from validationStruct import main as makeStruct
import pandas as pd

'''
This code will take in a set of filenames for FVCOM, ADCP, and TG data, and
create a validation struct from them. It will then append 
'''

# set up paths to FVCOM files, ADCP files, and TideGauge files to create struct
fvFiles = ['/EcoII/EcoEII_server_data_tree/workspace/simulated/FVCOM/dngrid/calibration/bottom_roughness/2D/0.0015/output/dngrid_0001.nc',
           '/EcoII/EcoEII_server_data_tree/workspace/simulated/FVCOM/dngrid/calibration/bottom_roughness/2D/0.0020/output/dngrid_0001.nc',
           '/EcoII/EcoEII_server_data_tree/workspace/simulated/FVCOM/dngrid/calibration/bottom_roughness/2D/0.0025/output/dngrid_0001.nc',
           '/EcoII/EcoEII_server_data_tree/workspace/simulated/FVCOM/dngrid/calibration/bottom_roughness/2D/0.002848/output/dngrid_0001.nc',
           '/EcoII/EcoEII_server_data_tree/workspace/simulated/FVCOM/dngrid/calibration/bottom_roughness/2D/0.0030/output/dngrid_0001.nc']
adcpFiles = ['/EcoII/EcoEII_server_data_tree/data/observed/GP/ADCP/Flow_GP-130620-BPa_avg5.mat',
             '/EcoII/EcoEII_server_data_tree/data/observed/GP/ADCP/Flow_GP-130620-BPb_avg5.mat']
tideFiles = ['/EcoII/EcoEII_server_data_tree/data/observed/GP/TideGauge/Westport_015892_20140325_1212_Z.mat',
             '/EcoII/EcoEII_server_data_tree/data/observed/DG/TideGauge/DigbyWharf_015893_20140115_2221_Z.mat']

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
struct = makeStruct(fvFiles, adcpFiles, tideFiles, isStation=False)
loadValidation(files)
valTable(files, vars)
