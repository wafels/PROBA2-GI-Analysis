"""
LYRA GI code
Implements the analysis of the LYRA GI 
"""
import kPyWavelet as wvt
import numpy as np

class lyra_gi:
    def __init__(self,data,dt):
        """Torrence and Compo based analysis
        data = time series of length N
        dt = sample cadence
        slevel = significance level
        dj = the spacing between discrete scales. Default is 0.125.
            A smaller # will give better scale resolution, but be slower to plot.
        s0 = the smallest scale of the wavelet.  Default is 2*DT.
        J  = the # of scales minus one. Scales range from S0 up to S0*2^(J*DJ),
            to give a total of (J+1) scales. Default is J = (LOG2(N DT/S0))/DJ.
        """
        self.data = data
        self.dt = dt
        self.slevel = 0.95
        self.s0 = 2.0*self.dt
        self.dj = 0.25
        self.J = -1
        self.N = data.size
        self.std = data.std()
        self.std2 = self.std ** 2
        self.normed = (self.data - self.data.mean())/self.std
        self.alpha = 0.0

    def transform(self):

        # Do the wavelet transform
        self.wave, self.scales, self.freqs, self.coi, self.fft, self.fftfreqs = wvt.wavelet.cwt(self.normed, self.dt, self.dj, self.s0, self.J, self.mother)

        # Inverse wavelet transform
        self.iwave = wvt.wavelet.icwt(self.wave, self.scales, self.dt, self.dj, self.mother)

        self.power = (abs(self.wave)) ** 2             # Normalized wavelet power spectrum
        self.fft_power = self.std2 * abs(self.fft) ** 2     # FFT power spectrum
        self.period = 1. / self.freqs                  # Periods

        self.signif, self.fft_theor = wvt.wavelet.significance(1.0, self.dt, self.scales, 0, self.alpha, significance_level=self.slevel, wavelet=self.mother)
        sig = (self.signif * np.ones((self.N, 1))).transpose()
        self.sig = self.power / sig                # Where ratio > 1, power is significant

        # Calculates the global wavelet spectrum and determines its significance level.
        self.glbl_power = self.std2 * self.power.mean(axis=1)
        self.dof = self.N - self.scales                     # Correction for padding at edges
        self.glbl_signif, tmp = wvt.wavelet.significance(self.std2, self.dt, self.scales, 1, self.alpha, significance_level=self.slevel, dof=self.dof, wavelet=self.mother)


    def neupert(self):
        """Implement the "Neupert operator" - this smooths the time series by the
        Gaussian width and takes the derivative simultaneously.  Implemented using
        the Torrence and Compo first derivative of Gaussian wavelet.
        """
        self.mother = wvt.wavelet.DOG(1)          # Neupert operator - first derivative of Gaussian
        self.transform()

    def countFlares(self):
        """Count the number of flare events in a LYRA time series.
        """
        self.mother = wvt.wavelet.DOG(2)
        self.transform()
        
        
        