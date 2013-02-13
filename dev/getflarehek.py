"""Example analysis script"""

import proba2gi
from sunpy.lightcurve import LYRALightCurve
from sunpy.time import TimeRange, parse_time
from datetime import timedelta
import pandas
from matplotlib import pyplot as plt
import numpy as np
from scipy.stats import ks_2samp
import pickle
import os


def main():

    functions = ['aggvarFit', 'diffvarFit', 'absvalFit', 'rsFit', 'higuchiFit']
    ts_types = ["no_spike", "between_spikes", "after_flare", "before_flare"]
    
    resample_size = 500
    resample_size = 'native_cadence'
    resample_size_string = str(resample_size)

    h = dict.fromkeys(ts_types,[])
    for key in h.keys():
        h[key] = {"aggvarFit":[],
                   'diffvarFit':[],
                   'absvalFit':[],
                   'rsFit':[],
                   'higuchiFit':[]}


    tstart = parse_time('2012/06/08')
    tend = parse_time('2012/07/08')

    tinitial = tstart
    while tstart <= tend:
        results = do_hurst1_for_one_day(tstart, resample_size, function=functions)
 
    # Simple analysis of pre and post flare Hurst components
    # Unpack the results into 3 types - before flare, after flare and between
    # spikes.  Compare the population of results using two-sided Kolmogorov-
    # Smirnov test

        for ts_type in results.keys():
            all_ts = results[ts_type]
            for ts in all_ts:
                for f in ts.keys():
                    if ts[f] is not None:
                        h_value = ts[f].do_slot("hurst")[0][0]
                        if h_value < 1.0 and h_value > 0.0:
                            h[ts_type][f].append(h_value)
        # Save the data
        directory = '/Users/ireland/proba2gi/pickle/'+ resample_size_string + '/'
        if not os.path.isdir(directory):
            os.makedirs(directory)
        filepath =  directory + \
            tinitial.strftime("%Y%m%d_%H%M%S") + '__' + \
            tstart.strftime("%Y%m%d_%H%M%S") + '.hurst.proba2gi.'+resample_size_string+'.pickle'
        pickle.dump(h, open( filepath, "wb" ))

        # Advance
        tstart = tstart + timedelta(days=1)

        # Do the two-sided K-S test
        #for type1 in h.keys():
        #    for type2 in h.keys():
        #        kstest = ks_2samp(np.array(h[type1]),np.array(h[type2]))
        #        print type1, len(h[type1]), type2, len(h[type2]), kstest
    


def do_hurst1_for_one_day(date, resample_size, function=['aggvarFit',
                                          'diffvarFit',
                                          'absvalFit',
                                          'rsFit',
                                          'higuchiFit']):
    minimum_length = 10000
    # Acquire all the relevant data
    gidata = proba2gi.GIData(date)
    #gidata.plot(extract='CHANNEL4', show_frm='combine', show_spike=True)
    #event_all_times = gidata.onoff(frm_name='combine').times()
    raw_no_event_times = gidata.onoff(frm_name='combine').complement().times()
    no_event_times = []
    for tr in raw_no_event_times:
        hour_part = tr.start().hour
        if hour_part >= 6:
            no_event_times.append(tr)


    # Go through each time range and perform the Hurst analyses    
    hurst_results = {"no_spike":[], "between_spikes":[],
                    "after_flare":[], "before_flare":[]}
    all_spike_times = []
    for i,tr in enumerate(no_event_times):
        lc = gidata.lyra.truncate(tr).extract('CHANNEL3')
        spike_times = []
        if len(lc.data) > 2:
        # Look for spikes in the time series: uses time-series, not lightcurves
            spike_times = proba2gi.find_spike(lc.data)
            if spike_times is not None:
                for st in spike_times:
                    if st.start().hour >= 6:
                        all_spike_times.append(st)

        # Split the time series into sections; each section does not contain 
        # a spike.  Uses time-series, not lightcurves
        raw_despiked = proba2gi.split_timeseries(lc.data,spike_times)
        
        # Filter the time-series to make sure there are enough points
        despiked = []
        for z in raw_despiked:
            if len(z) >= minimum_length:
                despiked.append(z)

        # Perform the analyses
        # Analysis 1
        # Calculate the Hurst exponent for the time series
        for j,newlc in enumerate(despiked):
            # newlc.data = np.random.randn(len(newlc))
            # resample the data to remove the effects of instrumental noise
            # resampled = newlc.resample('1s',how='mean',)
            if resample_size != 'native_cadence':
                resample_size_string = str(resample_size)+'L'
                resampled = newlc.resample(resample_size_string,how='sum')
            else:
                resampled = newlc
            # write out a csv file
            
            n = round(len(newlc)/(1.0*len(resampled)))
            # Store all the results.  i = 0 indicates the first
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
            # strictly ordered by time.

            if i != 0:
                # Drop the first time-series since we don't know its status -
                # before or after a flare???
                
                # This time series spans the range from after a flare to
                # before a flare with no spike in between
                if len(despiked) == 1:
                    results = proba2gi.hurst_fArma(resampled, function=function, levels=10)
                    hurst_results["no_spike"].append(results)
                
                # Two time-series are found if one spike is found in the parent
                # time-series.
                if len(despiked) == 2:
                    if j == 0:
                        results = proba2gi.hurst_fArma(resampled[0:minimum_length/n], function=function, levels=10)
                        hurst_results["after_flare"].append(results)
                        resampled.to_csv('/Users/ireland/proba2gi/csv/'+date.strftime("%Y%m%d_%H%M%S")+'_'+str(i)+'_'+str(j)+'.csv')
                    if j == 1:
                        results = proba2gi.hurst_fArma(resampled[-minimum_length/n:], function=function, levels=10)
                        hurst_results["before_flare"].append(results)
                if len(despiked) > 2:
                    if j == 0:
                        results = proba2gi.hurst_fArma(resampled[0:minimum_length/n], function=function, levels=10)
                        hurst_results["after_flare"].append(results)
                    if j >= 1 and j < len(despiked)-1:
                        results = proba2gi.hurst_fArma(resampled, function=function, levels=10)
                        hurst_results["between_spikes"].append(results)
                    if j == len(despiked)-1:
                        results = proba2gi.hurst_fArma(resampled[-minimum_length/n:], function=function, levels=10)
                        hurst_results["before_flare"].append(results)

    return hurst_results

        #for f in function:
        #    output = hurst[f]
        #    if output is not None:
        #        print('Hurst exponent from '+f)
        #        print(output.do_slot("hurst")[0])
        #        print('Standard error from '+f)
        #        print(output.do_slot("hurst")[2][1][1])


def analyze_hurst1(h1,f):
    """Plot and analyze the pre and post flare Hurst results"""
    style = {'before_flare':{"ecolor":'r',"marker":'s',"mfc":"r"},
              'after_flare':{"ecolor":'g',"marker":'D',"mfc":"g"}}
    hdf = pandas.DataFrame()
    for x in ['before_flare','after_flare']:
        hurst = []
        hurst_error = []
        time = []
        for element in h1[x]:
            bit = element["hurst1"][f]
            if bit is not None:
                hurst.append(bit.do_slot("hurst")[0][0])
                hurst_error.append(bit.do_slot("hurst")[2][1][1])
                time.append(element["ts"].index[0])
        hdf[x] = pandas.Series(hurst,index=time)
        plt.plot(time, hurst, style[x]["ecolor"]+"o", label=x)
        plt.errorbar(time,hurst, yerr=hurst_error, fmt = None,
                     ecolor=style[x]["ecolor"],
                     marker=style[x]["marker"])
        plt.axhline(1.0)
        plt.axhline(0.5)
        plt.legend()

if __name__ == '__main__':
    main()

"""
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
"""