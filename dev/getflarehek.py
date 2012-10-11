"""Example analysis script"""

import proba2gi
from sunpy.lightcurve import LYRALightCurve
import numpy as np
from datetime import timedelta
from sunpy.time import TimeRange

def main():

    tstart = '2011/03/05'

    # Acquire the HEK data
    result = proba2gi.fevent(tstart, directory='~/Data/HEK/', verbose=True)

    # Get a pandas Series of logical values indicating when an event was 
    # detected by any detection method.  True indicates that a flare
    # was detected by at least one method, False indicates that no flare was
    # detected by any method.
    all_onoff = result.onoff(frm_name = 'combine')
    
    # Get the start and end times of when a flare from any detection method
    # was detected.  Extracts the start and end times from the pandas Series
    # of logical values defined above
    event_all_times = all_onoff.times()
    
    # Get the start and end times of when no flare was detected.  This is
    # done by using the complement of the flare Series defined above.
    no_event_times = all_onoff.complement().times()

    # Acquire the LYRA data
    lyra = LYRALightCurve.create(tstart)
    
    analysis_results = []

    # Go through each time range and perform the Hurst analyses
    for i,tr in enumerate(no_event_times):
        lc = lyra.truncate(tr).extract('CHANNEL4')
        
        # Look for spikes in the time series: uses time-series, not lightcurves
        spike_times = proba2gi.find_spike(lc.data)

        # Split the time series into sections; each section does not contain 
        # a spike.  Uses time-series, not lightcurves
        despiked = proba2gi.split_timeseries(lc.data,spike_times)
    
        # choose which analysis method to use
        function = ['aggvarFit','diffvarFit']

        # Perform the analyses
        hurst_results = []
        for j,newlc in enumerate(despiked):
            # Analysis 1
            # Calculate the Hurst exponent for the time series
            
            # resample the data to remove the effects of instrumental noise
            # resampled = newlc.resample('1s',how='mean',)
            resampled = newlc
        
            # Hurst analysis 1
            hurst1_results = proba2gi.hurst_fArma(resampled.data, 
                                         function=function, 
                                         levels=10 )
            # Analysis 2
            # Calculate the Hurst exponent in running subsections of the input
            # time series.  This is intended to look for changes in the Hurst
            # exponent of time-series as a function of time.  For example, does
            # the Hurst exponent change noticably and consistently before
            # flares?
            hurst2_results = []
            
            # Pick the duration of the sub-time series
            duration = timedelta(seconds=10)
            
            # Pick how far to jump forward in time for the next sub time-series
            # Can use this to overlap with the previous time-series
            advance = duration/2
            
            # Start the loop 
            extent = TimeRange(resampled.data.index[0],
                               resampled.data.index[0] + duration)
            while extent.end() <= resampled.end_time:

                hurst2 = proba2gi.hurst_fArma(resampled[extent.start(),extent.end()], 
                                              function=function, 
                                              levels=10 )
        
                # Store the analyzed time-series and its Hurst analysis
                hurst2_results.append( {"extent":extent,
                                        "hurst2":hurst2} )
                extent.extend(advance,advance)

            # Store all the results.  index = 0 indicates the first
            # time-series after the flare.  The largest number indicates
            # the last time-series before the flare
            hurst_results.append({"index":j,
                                  "ts":resampled,
                                  "hurst1":hurst1_results,
                                  "hurst2":hurst2_results})
        
        analysis_results.append({"index":i,
                                 "lyra":lyra,
                                 "hurst_results":hurst_results})

        #for f in function:
        #    output = hurst[f]
        #    if output is not None:
        #        print('Hurst exponent from '+f)
        #        print(output.do_slot("hurst")[0])
        #        print('Standard error from '+f)
        #        print(output.do_slot("hurst")[2][1][1])


if __name__ == '__main__':
    main()