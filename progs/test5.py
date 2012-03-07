"""
Test code that makes use of the lyra and kPyWavelet code.
"""
import lyra,lyra_gi
import matplotlib.pyplot as plt
import numpy as np

def main():
    lobj = lyra.lyra('2011/06/29')
    lobj.download()
    lobj.load()

    # 300 seconds worth of data summed up into 4 second bins
    s = lyra.subthensum(lobj,'2011/06/29 20:00',300,binsize = 4.0)

    channel = lyra.channel(s,4)

    analyse = lyra_gi.lyra_gi(channel.data, channel.dt)
    analyse.dj = 0.125
    analyse.countFlares()
    plt.figure(1)
    plt.imshow(analyse.wave.real,aspect = 'auto')

    analyse.neupert()
    plt.figure(2)
    plt.imshow(analyse.wave.real,aspect='auto')

if __name__ == '__main__':
    sys.exit(main())