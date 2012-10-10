import proba2gi
from sunpy.lightcurve import LYRALightCurve
import numpy as np

def main():

    tstart = '2011/03/05'

    result = proba2gi.fevent(tstart, directory='~/Data/HEK/', verbose=True)

    all_onoff = result.onoff(frm_name = 'combine')
    event_all_times = all_onoff.times()
    no_event_times = all_onoff.complement().times()
    lyra = LYRALightCurve.create(tstart)

# Get the section of data we want
    ts = lyra.data["CHANNEL4"][no_event_times[0].start():no_event_times[0].end()]

    spike_times = proba2gi.findspike(ts)
    
    tsnew = proba2gi.splitts(ts,spike_times)
  
    return tsnew

if __name__ == '__main__':
    main()