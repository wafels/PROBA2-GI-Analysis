"""Helpers for the PROBA 2 analysis"""

from sunpy.net import hek
from sunpy.time import parse_time
from sunpy.time.timerange import TimeRange
from sunpy.lightcurve import LogicalLightCurve
from sunpy.lightcurve import LYRALightCurve
from sunpy.lightcurve import LightCurve
from matplotlib import pyplot as plt
import numpy as np
import os
import datetime
import pickle
import pandas
from rpy2.robjects.packages import importr
import rpy2.robjects as robjects



class EventTimeRange(TimeRange):
    """Used to identify that this time range denotes the start and end time of
    an event."""
    pass

class SpikeTimeRange(TimeRange):
    """Used to identify that this time range denotes the start and end time of
    an event."""
    pass

class SpikeTimeStart(datetime.datetime):
    """Used to identify the start time of a spike"""
    pass

class SpikeTimeEnd(datetime.datetime):
    """Used to identify the end time of a spike"""
    pass

class EventTimeStart(datetime.datetime):
    """Used to identify the start time of an event"""
    pass

class EventTimeEnd(datetime.datetime):
    """Used to identify the end time of an event"""

def find_spike(ts, binsize='12s', factor=2.0,
            exclusion_timescale=datetime.timedelta(minutes=1),
              method=None):
    """Find a spike in the data and return its approximate start and end time"""
    if method is None:
        # Resample in bins of a given size
        tss = ts.resample(binsize, how='mean')
        tnew = tss - pandas.stats.moments.rolling_median(tss,10, center=True)
        # Rescale to the standard deviation
        rescaled = abs((tnew-tnew.mean())/tnew.std())
    
        # Find the times where the rescaled time-series is big.
        spike_times = (LogicalLightCurve(rescaled>factor)).times()
        
        # Extend the times a little bit to make sure we definitely exclude the
        # spike
        adjusted = []
        for tr in spike_times:
            adjusted_left = tr.start()-exclusion_timescale
            if adjusted_left < ts.index[0]:
                adjusted_left = ts.index[0]
            
            adjusted_right = tr.start()+exclusion_timescale
            if adjusted_right > ts.index[-1]:
                adjusted_right = ts.index[-1]

            adjusted = [SpikeTimeRange(adjusted_left, adjusted_right)]

    return adjusted

    

class GIData:
    def __init__(self, date, directory = '~/Data/', extract='CHANNEL4'):
        """Routine to acquire the relevant data for a particular day for the
        PROBA2 GI"""
        # Which date?
        self.date = date
        # Acquire the HEK data
        self.hek = fevent(self.date, directory=os.path.join(directory,'HEK/'), verbose=True)
        # Acquire the LYRA data
        self.lyra = LYRALightCurve.create(self.date)
        # Which channel?
        self.extract = extract
        # No event times
        self.no_event_times = self.hek.onoff(frm_name='combine').complement().times()
        # Event times
        self.event_times = self.hek.onoff(frm_name='combine').times()

        # Spikes
        self.all_spike_times =[]
        for i,tr in enumerate(self.no_event_times):
            lc = self.lyra.truncate(tr).extract(self.extract)
            if len(lc.data) > 2:
                # Look for spikes in the time series: uses time-series, not lightcurves
                spike_times = find_spike(lc.data)
                if spike_times is not None:
                    for st in spike_times:
                        self.all_spike_times.append(st)

    def onoff(self, frm_name='combine'):
        return self.hek.onoff(frm_name=frm_name)

    def plot(self, extract=None, show_frm=None, show_spike=False, show_before_after=False):

        if extract is None:
            self.lyra.plot()
        else:
            lc = self.lyra.extract(extract)
            lc.plot()

        if show_frm is not None:
            times = self.onoff(frm_name=show_frm).times()
            for tr in times:
                plt.axvspan(tr.start(), tr.end(), facecolor='green', alpha=0.5)
        
        if show_spike:
            for tr in self.all_spike_times:
                plt.axvspan(tr.start(), tr.end(), facecolor='black', alpha=0.75)
                
        if show_before_after:
            for event in self.event_times:
                current_minimum = datetime.timedelta(days=3)
                for spike_time in self.all_spike_times:
                    event_end_to_spike_start = spike_time.start() - event.end()
                    print current_minimum
                    if event_end_to_spike_start > datetime.timedelta():
                        if event_end_to_spike_start < current_minimum:
                            current_minimum = event_end_to_spike_start
                after_flare = TimeRange(event.end(), spike_time.start())
                lc.truncate(after_flare.start(), after_flare.end()).plot(style ='c-')

            for event in self.event_times:
                current_minimum = datetime.timedelta(days=3)
                for spike_time in self.all_spike_times:
                    spike_end_to_event_start = event.start() - spike_time.end()
                    if spike_end_to_event_start > datetime.timedelta():
                        if spike_end_to_event_start < current_minimum:
                            current_minimum = event.start() - spike_time.end()
                before_flare = TimeRange(spike_time.end(),event.start())
                lc.truncate(before_flare.start(), before_flare.end()).plot(style ='r-')
        

#
# Small routine to convert a python string to a R-object string
#
def ps2rs(x):
    return robjects.r("'"+x+"'")
#
# Define a function which interfaces with the R-based Hurst calculators of
# the package 'R'
#
def hurst_fArma(data, function=['aggvarFit'], levels=10, minnpts=3,
                cut_off=10**np.array([0.7,2.5]), moment=1,
                method=None, length=None, nbox=None, order=None,
                subseries=None, octave=None ):
    """ Calculate the Hurst exponent using the fArma code of R, accessed
        via rpy2"""
    
    fArma = importr("fArma")

    fArma_functions = ['aggvarFit','diffvarFit', 'absvalFit', 'higuchiFit',
                    'pengFit', 'rsFit', 'perFit', 'boxperFit', 'whittleFit',
                    'waveletFit']

    answer = {}
    for f in function:
        if f in fArma_functions:
            Rdata = robjects.vectors.FloatVector(data)
            Rcut_off = robjects.vectors.FloatVector(cut_off)
            
            if f == 'aggvarFit':
                try:
                    output = robjects.r.aggvarFit(Rdata,
                                                  cut_off=Rcut_off, 
                                                  levels=levels,
                                                  minnpts=minnpts)
                except:
                    print f
                    print('Algorithm failure')
                    print " "
                    output=None

            if f == 'diffvarFit':
                try:
                    output = robjects.r.diffvarFit(Rdata,
                                                   cut_off=Rcut_off,
                                                   levels=levels,
                                                   minnpts=minnpts)
                except:
                    print f
                    print('Algorithm failure')
                    print " "
                    output=None
                
            if f == 'absvalFit':
                try:
                    output = robjects.r.absvalFit(Rdata,
                                                   cut_off=Rcut_off,
                                                   levels=levels,
                                                   minnpts=minnpts)
                except:
                    print f
                    print('Algorithm failure')
                    print " "
                    output=None
                
            if f == 'higuchiFit':
                try:
                    output = robjects.r.higuchiFit(Rdata,
                                                   cut_off=Rcut_off,
                                                   levels=levels,
                                                   minnpts=minnpts)
                except:
                    print f
                    print('Algorithm failure')
                    print " "
                    output=None
                    
            if f == 'pengFit':
                if method is None:
                    method = 'mean'
                Rmethod = ps2rs(method)
                output = robjects.r.pengFit(Rdata, 
                                            cut_off=Rcut_off,
                                            levels=levels,
                                            minnpts=minnpts,
                                            method=Rmethod)
            if f == 'rsFit':
                try:
                    output = robjects.r.rsFit(Rdata,
                                                   cut_off=Rcut_off,
                                                   levels=levels,
                                                   minnpts=minnpts)
                except:
                    print f
                    print('Algorithm failure')
                    print " "
                    output=None
                    
            if f == 'perFit':
                if method is None:
                    method = 'per'
                Rmethod = ps2rs(method)
                output = robjects.r.perFit(Rdata,
                                           cut_off=Rcut_off,
                                           method=Rmethod)
            if f == 'boxperFit':
                if nbox is None:
                    nbox=1
                Rnbox=robjects.r(nbox)
                output = robjects.r.boxperFit(Rdata,
                                              nbox=Rnbox,
                                              cutoff=Rcut_off)
            if f == 'whittleFit':
                if order is None:
                    order=np.array([1.0,1.0])
                Rorder = robjects.vectors.FloatVector(order)
                    
                if subseries is None:
                    subseries = 1
                Rsubseries = robjects.r(subseries)

                if method is None:
                    method='fgn'
                Rmethod = ps2rs(method)
                
                output = robjects.r.whittleFit(Rdata,
                                               order=Rorder,
                                               subseries=Rsubseries,
                                               method=method)
            if f == 'waveletFit':
                if order is None:
                    order=2
                if octave is None:
                    octave=np.array([2.0,8.0])
                Roctave = robjects.vectors.FloatVector(order)
                output = robjects.r.waveletFit(Rdata,
                                               order=Rorder,
                                               octave=Roctave)
        answer[f] = output
    return answer
    
def exclude_timerange(ts,timerange):
    """Split the input timeseries into two smaller sub time-series that exclude 
    the time range"""
    return [ts[:timerange.start()],ts[timerange.end():]]

def split_timeseries(ts,timeranges):
    """Split the input timeseries into as many smaller sub-time-series as
    required"""

    # If no timerange is passed in, just return the time series
    if timeranges == []:
        return [ts]

    split =[]
    tsremainder = ts
    # Sort the input timeranges
    sorted_start_times = np.argsort([tr.start() for tr in timeranges])
    # Go through the sorted time ranges
    for i in range(0,len(sorted_start_times)):
        timerange = timeranges[i]
        ts_bits = exclude_timerange(tsremainder,timerange)
        split.append(ts_bits[0])
        tsremainder = ts_bits[1]
    # Remember to keep the last bit.
    split.append(tsremainder)

    return split

def hurst_analysis2(ts, duration = None, advance = None,**kwargs):
    hurst2_results = []

    # Pick the duration of the sub-time series
    #duration = timedelta(seconds=10)
            
    # Pick how far to jump forward in time for the next sub time-series
    # Can use this to overlap with the previous time-series
    #advance = duration/2
            
    # Start the loop 
    extent = TimeRange(ts.data.index[0],
                       ts.data.index[0] + duration)
    while extent.end() <= ts.data.index[-1]:
        hurst2 = hurst_fArma([extent.start(),extent.end()],kwargs)
        
        # Store the analyzed time-series and its Hurst analysis
        hurst2_results.append( {"extent":extent,"hurst2":hurst2} )
        extent.extend(advance,advance)

def hek_spike_summary(lc,hek_times,spike_times):
    lc.plot()
    for event_time in hek_times:
        plt.axvspan(event_time.start(), 
                    event_time.end(), facecolor='g', alpha=0.2)
    for spike_time in spike_times:
        plt.axvspan(spike_time.start(), 
                    spike_time.end(), facecolor='black', alpha=1.0)



def dowavelet(ts):
    """Peform a wavelet analysis of the time series to look for oscillations"""
    pass