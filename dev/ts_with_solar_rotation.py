import numpy as np
from matplotlib import pyplot as plt



def main():

    def mimic_solar_rotation(emission, imax, cadence):
        arcseconds_per_pixel=0.6
        
        arcsecond_per_second=240.0/(24.0*60*60)
        pixels_per_second = arcsecond_per_second / arcseconds_per_pixel
        
        index = 0
        current_pixel = 0
        data = []
        time_in_pixel = 0
        while index < imax:
            index = index + 1
            time_in_pixel = time_in_pixel + cadence
            decreasing = 1.0 - pixels_per_second*time_in_pixel
            increasing = pixels_per_second*time_in_pixel
            if decreasing > 0:
                data.append(decreasing*emission[current_pixel,index] + increasing*emission[current_pixel+1,index])
            else:
                # all of the current_pixel is gone - we have moved on to the next pixel
                time_in_pixel = 0.0
                current_pixel = current_pixel + 1
                increasing = pixels_per_second*time_in_pixel
                data.append((1+decreasing)*emission[current_pixel,index] + abs(decreasing)*emission[current_pixel+1,index])
        return data, current_pixel

    npixels = 1000
    imax = 2400
    cadence = 12.0
        
    gamma = 2.0
    emission = np.random.pareto(gamma-1.0,size=(npixels,2*imax))
    data, current_pixel = mimic_solar_rotation(emission, imax, cadence)
    pwr1 = (np.abs(np.fft.rfft(np.array(data))))**2
    norm1 = np.var(data)

    emission = np.random.randn(npixels,2*imax)
    data, current_pixel = mimic_solar_rotation(emission, imax, cadence)
    pwr2 = (np.abs(np.fft.rfft(np.array(data))))**2
    norm2 = np.var(data)


    freq = np.fft.fftfreq(len(data),cadence)
    pfreq = freq[freq>0]
    nfreq = len(pfreq)

    plt.ioff()
    fig = plt.figure(2)
    ax = fig.add_subplot(111)
    plt.plot(pfreq[1:nfreq], pwr1[1:nfreq]/norm1, 'g', label='Gaussian noise')
    plt.plot(pfreq[1:nfreq], pwr2[1:nfreq]/norm2, 'r', label='power law noise $\gamma=-$'+str(int(gamma)) )
    plt.xlabel('frequency (mHz)')
    plt.ylabel('normalized Fourier power')
    plt.title('Power spectra (normalized to variance)')
    plt.text(0.01,0.95,'mimicing solar rotation at disk center: '+str(int(cadence*len(data))) + ' seconds'+', # px = '+str(int(current_pixel)), transform=ax.transAxes, )
    plt.yscale('log')
    plt.xscale('log')
    plt.legend(loc=3)

    plt.show()

if __name__ == '__main__':
    main()
