"""
Test code that makes use of the lyra and kPyWavelet code.
"""
import lyra,lyra_gi
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
import scipy

lobj = lyra.lyra('2011/08/09')
lobj.download()
lobj.load()

# 300 seconds worth of data summed up into 4 second bins
s = lyra.sub(lobj,'2011/08/09 08:30',600)

channel = lyra.channel(s,4)

analyse = lyra_gi.lyra_gi(channel.data, channel.dt)
analyse.dj = 0.125
analyse.neupert()
plt.figure(1)
plt.plot(channel.time,channel.data)

this = 20
print 'Smoothing scale = ',analyse.scale[this]
lyra_deriv = analyse.wave.real[this,:]
plt.figure(2)
plt.plot(channel.time,lyra_deriv)
plt.xlabel = 'time (s)'
plt.ylabel = 'time derivative of LYRA flux'
    
 
