"""Re-doing the analysis to make it more flexible"""

from sunpy.lightcurve import LYRALightCurve
from sunpy.time import parse_time
from datetime import timedelta
from interrogate_hek import fevent
import proba2gi2



def main():

    hek_directory='~/Data/HEK'
    tstart = parse_time('2012/06/08')
    tend = parse_time('2012/07/08')
    channel='CHANNEL4'

    while tstart <= tend:
        # Get the HEK data
        hek = fevent(tstart, directory=hek_directory, verbose=True)
        
        # Get the time-ranges of when there is NO event
        non_event_times = hek.onoff(frm_name='combine').complement().times()
        
        # Get the PROBA2 data
        lyra = LYRALightCurve.create(tstart)
        
        # Get the spike times in the non flaring data
        spike_times=[]
        for tr in non_event_times:
            lyra_bit = lyra.data[channel][tr.start():tr.end()]
            spike_times = proba2gi2.find_spike(lyra_bit)
            if spike_times != []:
                spike_times.append(spike_times)
        
        # Combine the spike times and the non-flaring data
        times_list = 
        
        # Identify the time series that begin with a time which is the start of a non-event
        # time series, and end in a spike
        after_flare = []
        for i in range(len(times_list)):
            if (times_list[i] is EventTimeStart) and (times_list[i+1] is SpikeTimeStart):
                after_flare.append(TimeRange(times_list[i],times_list[i+1]))
        
        # Identify the time series that end with an event_start
        before_flare = []
        for i in range(len(times_list)):
            if (times_list[i] is SpikeTimeEnd) and (times_list[i+1] is EventTimeEnd):
                before_flare.append(TimeRange(times_list[i],times_list[i+1]))
        
        
        # Save these time-series.

        # Advance
        tstart = tstart + timedelta(days=1)

    # Read in the time series
    

if __name__ == '__main__':
    main()
