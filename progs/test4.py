"""
Test code that makes use of the lyra and kPyWavelet code.
"""
import lyra
import kPyWavelet as wvt
#import matplotlib.pyplot as plt
import pylab
import numpy as np
lobj = lyra.lyra('2011/06/29')
lobj.download()
lobj.load()

#ss = lyra.subthensum(lyra,'2011/06/29 20:00',300,binsize = 4.0)

# get 300 seconds worth of data
s = lyra.sub(lobj,'2011/06/29 20:00',300)



choose = 4
units = s.data.columns[choose].name + ' ('+s.data.columns[choose].unit+')'

ch = s.data.field(choose)[:]
title =  s.data.columns[choose].name + ' ('+s.data.columns[choose].unit+')' + str(lobj.tstart) + ' - ' + str(lobj.tend)
label = 'normalized'
xlabel = s.data.columns[0].name + ' ('+s.data.columns[0].unit+')'

avg1, avg2 = (2, 8)                  # Range of periods to average
slevel = 0.95                        # Significance level

std = ch.std()                      # Standard deviation
std2 = std ** 2                      # Variance
ch = (ch - ch.mean()) / std       # Calculating anomaly and normalizing

N = ch.size                         # Number of measurements
time = s.data.field(0)  # Time array in seconds

dj = 0.25                            # Four sub-octaves per octaves
s0 = -1 #2 * dt                      # Starting scale, here 6 months
J = -1 # 7 / dj                      # Seven powers of two with dj sub-octaves
alpha = 0.0                          # Lag-1 autocorrelation for white noise
dt = s.data.field(0)[1]-s.data.field(0)[0]
#alpha = np.correlate(var, var, 'same')
#alpha /= alpha.max()
#alpha = 0.5 * (alpha[N / 2 + 1] + alpha[N / 2 + 2] ** 0.5)
#
#
mother = wvt.wavelet.Morlet(6.)          # Morlet mother wavelet with wavenumber=6
#mother = wavelet.Mexican_hat()       # Mexican hat wavelet, or DOG with m=2
#mother = wavelet.Paul(4)             # Paul wavelet with order m=4

# Do the wavelet transform
wave, scales, freqs, coi, fft, fftfreqs = wvt.wavelet.cwt(ch, dt, dj, s0, J, mother)

# Inverse wavelet transform
iwave = wvt.wavelet.icwt(wave, scales, dt, dj, mother)


power = (abs(wave)) ** 2             # Normalized wavelet power spectrum
fft_power = std2 * abs(fft) ** 2     # FFT power spectrum
period = 1. / freqs                  # Periods

signif, fft_theor = wvt.wavelet.significance(1.0, dt, scales, 0, alpha, significance_level=slevel, wavelet=mother)
sig95 = (signif * np.ones((N, 1))).transpose()
sig95 = power / sig95                # Where ratio > 1, power is significant

# Calculates the global wavelet spectrum and determines its significance level.
glbl_power = std2 * power.mean(axis=1)
dof = N - scales                     # Correction for padding at edges
glbl_signif, tmp = wvt.wavelet.significance(std2, dt, scales, 1, alpha, significance_level=slevel, dof=dof, wavelet=mother)

# Scale average between avg1 and avg2 periods and significance level
sel = pylab.find((period >= avg1) & (period < avg2))
Cdelta = mother.cdelta
scale_avg = (scales * np.ones((N, 1))).transpose()
# As in Torrence and Compo (1998) equation 24
scale_avg = power / scale_avg
scale_avg = std2 * dj * dt / Cdelta * scale_avg[sel, :].sum(axis=0)
scale_avg_signif, tmp = wvt.wavelet.significance(std2, dt, scales, 2, alpha, significance_level=slevel, dof=[scales[sel[0]], scales[sel[-1]]], wavelet=mother)



# The following routines plot the results in four different subplots containing
# the original series anomaly, the wavelet power spectrum, the global wavelet
# and Fourier spectra and finally the range averaged wavelet spectrum. In all
# sub-plots the significance levels are either included as dotted lines or as
# filled contour lines.
pylab.close('all')
fontsize = 'medium'
params = {'text.fontsize': fontsize,
          'xtick.labelsize': fontsize,
          'ytick.labelsize': fontsize,
          'axes.titlesize': fontsize,
          'text.usetex': True
         }
pylab.rcParams.update(params)          # Plot parameters
figprops = dict(figsize=(11, 8), dpi=72)
fig = pylab.figure(**figprops)

# First sub-plot, the original time series anomaly.
ax = pylab.axes([0.1, 0.75, 0.65, 0.2])
ax.plot(time, iwave, '-', linewidth=1, color=[0.5, 0.5, 0.5])
ax.plot(time, ch, 'k', linewidth=1.5)
ax.set_title('a) %s' % (title, ))
ax.set_ylabel(label)
ax.set_xlabel(xlabel)

# Second sub-plot, the normalized wavelet power spectrum and significance level
# contour lines and cone of influece hatched area.
bx = pylab.axes([0.1, 0.37, 0.65, 0.28], sharex=ax)
pylab.imshow(sig95,aspect = 'auto',extent = (time[0],time[-1],period[-1],period[0]))
bx.contour(time,period,sig95,[1.0])
bx.set_title('b) %s Wavelet Power Spectrum (%s)' % (label, mother.name))
bx.set_ylabel('Period (secs)')
bx.set_xlabel(xlabel)
bx.fill(np.concatenate([time[:1]-dt, time, time[-1:]+dt, time[-1:]+dt,
        time[:1]-dt, time[:1]-dt]), np.log2(np.concatenate([[1e-9], coi,
        [1e-9], period[-1:], period[-1:], [1e-9]])), 'k', alpha='0.3',
        hatch='x')

levels = [0.0625, 0.125, 0.25, 0.5, 1, 2, 4, 8, 16]
bx.contourf(time, np.log2(period), np.log2(power), np.log2(levels),extend='both')
bx.contour(time, np.log2(period), sig95, [-99, 1], colors='k',linewidths=2.)
bx.fill(np.concatenate([time[:1]-dt, time, time[-1:]+dt, time[-1:]+dt,
        time[:1]-dt, time[:1]-dt]), np.log2(np.concatenate([[1e-9], coi,
        [1e-9], period[-1:], period[-1:], [1e-9]])), 'k', alpha='0.3',
        hatch='x')
bx.set_title('b) %s Wavelet Power Spectrum (%s)' % (label, mother.name))
bx.set_ylabel('Period (secs)')
Yticks = 2 ** np.arange(np.ceil(np.log2(period.min())),
                           np.ceil(np.log2(period.max())))
bx.set_yticks(np.log2(Yticks))
bx.set_yticklabels(Yticks)
bx.invert_yaxis()

"""

# Third sub-plot, the global wavelet and Fourier power spectra and theoretical
# noise spectra.
cx = pylab.axes([0.77, 0.37, 0.2, 0.28], sharey=bx)
cx.plot(glbl_signif, np.log2(period), 'k--')
cx.plot(fft_power, np.log2(1./fftfreqs), '-', color=[0.7, 0.7, 0.7],
        linewidth=1.)
cx.plot(glbl_power, np.log2(period), 'k-', linewidth=1.5)
cx.set_title('c) Global Wavelet Spectrum')
if units != '':
    cx.set_xlabel(r'Power [$%s^2$]' % (units, ))
else:
    cx.set_xlabel(r'Power')
#cx.set_xlim([0, glbl_power.max() + std2])
cx.set_ylim(np.log2([period.min(), period.max()]))
cx.set_yticks(np.log2(Yticks))
cx.set_yticklabels(Yticks)
pylab.setp(cx.get_yticklabels(), visible=False)
cx.invert_yaxis()

# Fourth sub-plot, the scale averaged wavelet spectrum as determined by the
# avg1 and avg2 parameters
dx = pylab.axes([0.1, 0.07, 0.65, 0.2], sharex=ax)
dx.axhline(scale_avg_signif, color='k', linestyle='--', linewidth=1.)
dx.plot(time, scale_avg, 'k-', linewidth=1.5)
dx.set_title('d) $%d$-$%d$ year scale-averaged power' % (avg1, avg2))
dx.set_xlabel('Time (year)')
if units != '':
    dx.set_ylabel(r'Average variance [$%s$]' % (units, ))
else:
    dx.set_ylabel(r'Average variance')
#
ax.set_xlim([time.min(), time.max()])
#
pylab.draw()
pylab.show()

# That's all folks!
"""