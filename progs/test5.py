"""
Test code that makes use of the lyra and kPyWavelet code.
"""
import lyra,lyra_gi
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import odeint
import scipy

def main():
    lobj = lyra.lyra('2011/08/09')
    lobj.download()
    lobj.load()
    #lobj.plot()

    # 300 seconds worth of data summed up into 4 second bins
    s = lyra.subthensum(lobj,'2011/08/09 08:30',3600,binsize = 4.0)

    channel = lyra.channel(s,4)

    analyse = lyra_gi.lyra_gi(channel.data, channel.dt)
    analyse.dj = 0.125
    analyse.neupert()
    plt.figure(1)
    plt.plot(channel.time,channel.data)
    
    lyra_deriv = analyse.wave.real[0,:]
    plt.figure(2)
    plt.plot(channel.time,lyra_deriv)
    plt.xlabel = 'time (s)'
    plt.ylabel = 'time derivative of LYRA flux'
    
    def zzz(u,t,Clyra,lyra_deriv): #defines the system of odes
        return (lyra_deriv-Clyra*u) #the derivatives of u
    
    Clyra = 1.0
    u0 = 1.0
    hxr = odeint(zzz,u0,channel.time,args=(Clyra,lyra_deriv))
    
    plt.figure(3)
    plt.plot(channel.time,hxr)
    plt.xlabel = 'time (s)'
    plt.ylabel = 'recovered hard x-ray flux'
    #analyse.neupert()
    #plt.figure(2)
    #plt.imshow(analyse.wave.real,aspect='auto')

if __name__ == '__main__':
    sys.exit(main())