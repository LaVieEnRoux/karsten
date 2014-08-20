from __future__ import division
from save_FlowFile_BPFormat import *
from EnsembleData_FlowFile import *
from nan_AboveSurf import *
import sys
import scipy.io as sio

if __name__ == '__main__':

    if (len(sys.argv) == 1):
	filename = '/EcoII/EcoEII_server_data_tree/data/observed/GP/ADCP/' + \
                   'GP-120726-BPd_raw.mat'
    else:
	filename = sys.argv[1]

    data = rawADCP(filename)
    rawdata = rawADCP(filename)
    adcp = data.adcp
    params = data.saveparams
    rbr = Struct(**data.rbr)
    saveDict = \
        save_FlowFile_BPFormat(data.fileinfo, adcp, rbr, params, data.options)

    data = saveDict['data']
    pres = saveDict['pres']
    time = saveDict['time']
    
    # fields for data to insert NaNs
    fields = ['mag_signed_vel','east_vel','north_vel','vert_vel','error_vel',
              'dir_vel']

    # eliminate NaNs above surface
    for field in fields:
        print 'Adding NaNs for ' + field
        nan_AboveSurf(data[field], data['bins'], pres['surf'])

    # calculate ensemble averages
    t_ens = 600 # ten minute averaging
    time_ens, data_ens, pres_ens = EnsembleData_FlowFile(t_ens, time, data,
                                                         pres)

    saveDict['data'] = data_ens
    saveDict['pres'] = pres_ens
    saveDict['time'] = time_ens
    saveDict['data']['bins'] = data['bins']

    # parse ADCP name
    ADCP_name = ((filename.split('/')[-1]).split('.')[0]).split('_raw')[0]

    print ADCP_name

    sio.savemat(ADCP_name + '_avg_{}min.mat'.format(int(t_ens / 60)), saveDict)       
