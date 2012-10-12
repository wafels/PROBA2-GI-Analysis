"""Example analysis script"""

import proba2gi
from sunpy.lightcurve import LYRALightCurve
import numpy as np
from datetime import timedelta
from sunpy.time import TimeRange

def main():

    tstart = '2011/03/05'

    # Acquire the HEK data
    hekdata = proba2gi.fevent(tstart, directory='~/Data/HEK/', verbose=True)

    # Get a pandas Series of logical values indicating when an event was 
    # detected by any detection method.  True indicates that a flare
    # was detected by at least one method, False indicates that no flare was
    # detected by any method.
    all_onoff = hekdata.onoff(frm_name = 'combine')
    
    # Get the start and end times of when a flare from any detection method
    # was detected.  Extracts the start and end times from the pandas Series
    # of logical values defined above
    event_all_times = all_onoff.times()
    
    # Get the start and end times of when no flare was detected.  This is
    # done by using the complement of the flare Series defined above.
    no_event_times = all_onoff.complement().times()

    # Acquire the LYRA data
    lyra = LYRALightCurve.create(tstart)

    # Go through each time range and perform the Hurst analyses    
    hurst_results = {"no_spike":[], "after_flare":[], "before_flare":[]}
    all_spike_times = []
    for i,tr in enumerate(no_event_times):
        lc = lyra.truncate(tr).extract('CHANNEL4')
        
        # Look for spikes in the time series: uses time-series, not lightcurves
        spike_times = proba2gi.find_spike(lc.data)
        if spike_times is not None:
            for st in spike_times:
                all_spike_times.append(st)

        # Split the time series into sections; each section does not contain 
        # a spike.  Uses time-series, not lightcurves
        despiked = proba2gi.split_timeseries(lc.data,spike_times)
    
        # choose which analysis method to use
        function = ['aggvarFit','diffvarFit','waveletFit']

        # Perform the analyses
        for j,newlc in enumerate(despiked):
            # Analysis 1
            # Calculate the Hurst exponent for the time series
            
            # resample the data to remove the effects of instrumental noise
            # resampled = newlc.resample('1s',how='mean',)
            resampled = newlc
        
            # Hurst analysis 1
            hurst1_results = proba2gi.hurst_fArma(resampled, 
                                                  function=function, 
                                                  levels=10 )
            print hurst1_results["aggvarFit"].do_slot("hurst")[0]
            print hurst1_results["waveletFit"].do_slot("hurst")[0]
            # Analysis 2
            # Calculate the Hurst exponent in running subsections of the input
            # time series.  This is intended to look for changes in the Hurst
            # exponent of time-series as a function of time.  For example, does
            # the Hurst exponent change noticably and consistently before
            # flares?
            #hurst2_results = proba2gi.hurst_analysis2(resampled,
            #                                          duration = timedelta(seconds=10),
            #                                          advance = timedelta(seconds=5), 
            #                                          function=function, 
            #                                          levels=10 )
            hurst2_results = None

            # Store all the results.  index = 0 indicates the first
            # time-series after the flare, except when we are looking at the
            # very first segment.  The largest number indicates
            # the last time-series before the flare
            # The index i refers to the interflare time series
            # The index j refers to how this time series has been split up
            # into smaller sections that avoid spikes.  If there is an
            # interflare timeseries 'i' that has only one subindex j=0
            # then no spikes occured in time-series 'i'.
            # For all i >= 1, j = 0 gives the sub time-series directly after
            # the flare, and the maximum value of 'k' for (i,k) where i is fixed
            # gives you the time-series immediately preceding a flare.
            # We are relying on the series returned by despike as being
            # strinctly ordered by time.
            
            # If the despiked time-series has only one entry, then no spike
            # occurred
            compiled_results = {"ts":resampled,
                                "hurst1":hurst1_results,
                                "hurst2":hurst2_results}
            if i != 0:
                # Drop the first time-series since we don't know its status -
                # before or after a flare???
                
                # This time series spans the range from after a flare to
                # before a flare with no spike in between
                if len(despiked) == 1:
                    hurst_results["no_spike"].append(compiled_results)
                
                # Two time-series are found if one spike is found in the parent
                # time-series.
                if len(despiked) >= 2:
                    if j == 0:
                        hurst_results["after_flare"].append(compiled_results)
                    if j == len(despiked)-1:
                        hurst_results["before_flare"].append(compiled_results)

    return hekdata, lyra, event_all_times, no_event_times, all_spike_times, hurst_results

        #for f in function:
        #    output = hurst[f]
        #    if output is not None:
        #        print('Hurst exponent from '+f)
        #        print(output.do_slot("hurst")[0])
        #        print('Standard error from '+f)
        #        print(output.do_slot("hurst")[2][1][1])
def analyze_hurst1(h1):
    pass


if __name__ == '__main__':
    main()