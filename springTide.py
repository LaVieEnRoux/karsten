from utide import ut_reconstr
from datetime import *
import cPickle as pickle
import matplotlib.pyplot as plt
import numpy as np

def datetime2matlabdn(dt):
   ord = dt.toordinal()
   mdn = dt + timedelta(days = 366)
   frac = (dt-datetime(dt.year,dt.month,dt.day,0,0,0)).seconds / (24.0 * 60.0 * 60.0)
   return mdn.toordinal() + frac

# load in struct harmonics
filename = '/EcoII/EcoEII_server_data_tree/code/wesCode/project/june_2013_3D_station.p'
file = open(filename, 'rb')
struct = pickle.load(file)
site = struct['june_2013_3D_station'][0]
harmonics = site['vel_mod_harmonics']

# create datenums and reconstruct
start = datetime(2013, 3, 1, 0, 0, 0)
step = timedelta(minutes=10)
steps = 6 * 24 * 90
dt = start + np.arange(steps) * step
dn = np.zeros(dt.size)
for i, v in enumerate(dt):
    dn[i] = datetime2matlabdn(v)
print 
pred_uv = ut_reconstr(dn, harmonics)
speed = np.sqrt(pred_uv[0]**2 + pred_uv[1]**2)

# plot
plt.plot(dt, speed)
plt.show()
