# Program to test red noise stuff

import sunpy
import numpy as np
from matplotlib import pyplot as plt

mc = sunpy.make_map('~/Data/rednoise/test_171', type='cube')
# size of the map
sh = mc[0].shape

# pick an element
a = int(np.rint( (sh[0]-1)*np.random.uniform() ))
b = int(np.rint( (sh[1]-1)*np.random.uniform() ))



# 304 data
em1 = mc.get_lightcurve_by_array_index(a,b)
name = mc[0].name
d = em1.data[name]
pwr1 = (np.abs(np.fft.rfft(d)))**2
norm1 = np.array(np.var(d))[0][0]


# Number of elements
n = len(d)


# Frequencies
freq = np.fft.fftfreq(n, 12.0)
pfreq = freq[freq>0]
nfreq = len(pfreq)

# Gaussian Noise
gaussian = np.random.randn(n)
pwr2 = (np.abs(np.fft.rfft(gaussian)))**2
norm2 = np.var(gaussian)

# Power law noise
gamma = 2.0
pln = np.random.pareto(gamma-1.0,size=n)
pwr3 = (np.abs(np.fft.rfft(pln)))**2
norm3 = np.var(pln)


# Plot comparison power spectra
plt.figure(1)
plt.plot(pfreq[1:nfreq], pwr1[1:nfreq]/norm1, label=mc[0].name+' off limb element ('+str(a)+','+str(b)+')')
plt.plot(pfreq[1:nfreq], pwr2[1:nfreq]/norm2, label='Gaussian noise')
plt.plot(pfreq[1:nfreq], pwr3[1:nfreq]/norm3, label='power law noise $\gamma=-$'+str(int(gamma)) )

plt.legend(loc=3)
plt.xlabel('frequency (mHz)')
plt.ylabel('normalized Fourier power')
plt.title('Comparison of power spectra (normalized to variance)')

plt.yscale('log')
plt.xscale('log')
plt.show()

