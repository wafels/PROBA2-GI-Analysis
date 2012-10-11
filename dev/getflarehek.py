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
    # Get the section of data we want
    
    result = []
    for tr in no_event_times:
        ts = lyra.data["CHANNEL4"][tr.start():tr.end()]
        
        # Look for spikes in the time series
        spike_times = proba2gi.find_spike(ts)

        # Split the time series into sections; each section does not contain a spike
        despiked = proba2gi.split_timeseries(ts,spike_times,
                                             label_last='just_before_flare',
                                             label_first='just_after_flare')
    
        # choose which analysis method to use
        function = ['aggvarFit','diffvarFit']

        # Perform the analyses
        analysis_results = []
        for newts in despiked:
            # Analysis 1
            # Calculate the Hurst exponent for the time series
            
            # resample the data to remove the effects of instrumental noise
            # resampled = newts.resample('1s',how='mean',)
            resampled = newts
        
            # Hurst analysis 1
            hurst1_results = proba2gi.hurst_fArma(resampled, 
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
            extent = TimeRange(resampled.start_time,
                               resampled.start_time + duration)
            while extent.t2 <= resampled.end_time:

                hurst2 = proba2gi.hurst_fArma(resampled[extent.t1,extent.t2], 
                                              function=function, 
                                              levels=10 )
        
                # Store the analyzed time-series and its Hurst analysis
                hurst2_results.append( {"t1":extent.t1,
                                        "t2":extent.t2,
                                        "hurst2":hurst2} )
                extent.extend(advance,advance)

            # Store all the results
            analysis_results.append({"ts":resampled,
                                     "hurst1":hurst1_results,
                                     "hurst2":hurst2_results})

        #for f in function:
        #    output = hurst[f]
        #    if output is not None:
        #        print('Hurst exponent from '+f)
        #        print(output.do_slot("hurst")[0])
        #        print('Standard error from '+f)
        #        print(output.do_slot("hurst")[2][1][1])
        

    # subset the time-series for each event

        result.append(do_hurst(ts))
 

if __name__ == '__main__':
    main()