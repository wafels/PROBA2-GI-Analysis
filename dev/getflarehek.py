"""Example analysis script"""

import proba2gi
from sunpy.lightcurve import LYRALightCurve
import numpy as np

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
    ts = lyra.data["CHANNEL4"][no_event_times[0].start():no_event_times[0].end()]

    # Look for spikes in the time series
    spike_times = proba2gi.findspike(ts)

    # Split the time series into sections; each section does not contain a spike
    despiked = proba2gi.splitts(ts,spike_times)
    
    # choose which analysis method to use
    function = ['aggvarFit','diffvarFit']

    # Keep the results
    results = []

    # Perform the analysis
    for newts in despiked:
    
        hurst = proba2gi.hurst_fArma( np.array(newts), 
                                       function=function, 
                                       levels=10 )
        results.append(hurst)

        for f in function:
            output = hurst[f]
            print('Hurst exponent from '+f)
            print(output.do_slot("hurst")[0])
            print('Standard error from '+f)
            print(output.do_slot("hurst")[2][1][1])
        

    # subset the time-series for each event

    return results

if __name__ == '__main__':
    main()