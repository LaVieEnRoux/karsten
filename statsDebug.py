import numpy as np
from tidalStats import TidalStats
from datetime import datetime, timedelta

# test of the tidalStats class with known data

n = 100
data_1, data_2 = np.zeros(n), np.zeros(n)
for i in np.arange(n):
    data_1[i] = i**2
    data_2[i] = i ** 3

start = datetime(1994, 04, 20)
step = timedelta(minutes=10)

stats = TidalStats(data_1, data_2, step, start)

print stats.getStats()
stats.plotRegression(stats.linReg())
