"""
Test code that makes use of the lyra and kPyWavelet code.
"""
import lyra,lyra_gi
import matplotlib.pyplot as plt
import numpy as np

lobj = lyra.lyra('2011/06/29')
lobj.download()
lobj.load()

# 300 seconds worth of data summed up into 4 second bins
s = lyra.subthensum(lobj,'2011/06/29 20:00',300,binsize = 4.0)

channel = lyra.channel(s,4)

data = np.ones(shape=(300,),dtype=np.float32)
data[150]=3.0
dt = 1.0

analyse = lyra_gi.lyra_gi(data, dt)
analyse.dj = 0.125
analyse.countFlares()
