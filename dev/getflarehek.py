from sunpy.net import hek
from sunpy.time import parse_time
from sunpy import lightcurve
import os
import datetime
import pickle
import pandas
import matplotlib.pyplot as plt

def hek_acquire(tstart, tend, EventType='FL', directory = '~', verbose = False, filename = None):
    """acquire HEK results from file, or download and save them"""
    
    # standard extension
    extension = '.hek.' + EventType + '.pickle'
    # create a client
    client = hek.HEKClient()
    
    # create a filename if none passed
    if filename == None:
        filename = tstart.strftime("%Y%m%d_%H%M%S") + '__' + tend.strftime("%Y%m%d_%H%M%S") + extension

    # get the full file path
    filepath = os.path.join(os.path.expanduser(directory), filename)
    
    # either load the data or go get it
    if os.path.isfile(filepath):
        if verbose:
            print('Loading local file: ' + filepath)
        result = pickle.load(open( filepath, "rb" ) )
    else:
        if verbose:
            print('Querying HEK for data and will save to following file: '+ filepath)
        result = client.query(hek.attrs.Time(tstart,tend), hek.attrs.EventType(EventType))
        pickle.dump(result, open( filepath, "wb" ))

    return result

def hek_detection_times(tstart,tend,result, all_frms_name = 'All FRMs', number_name = 'number'):

    # get the unique feature recognition methods
    hek_frms = list( set( [ x['frm_name'] for x in result ] ) )
    
    # Get a list of datetime objects spanning the requested time range
    hek_times = pandas.DateRange(tstart, tend, offset = pandas.datetools.Second())
    
    # Create a dictionary that will be the pandas dataframe that will not when a
    # a flare in each method was detected.
    
    hek_detections = {}
    for frm in hek_frms:
        hek_detections[frm] = False
    hek_detections[all_frms_name] = False
    hek_detections[number_name] = 0.0
    # Create the pandas dataframe
    detected_times = pandas.DataFrame(hek_detections, index = hek_times)

    # For each result get when it occurred. Classify by feature recognition method.
    for x in result:
        event_starttime = max( (parse_time(x['event_starttime']), hek_times[0]) )
        event_endtime =   min( (parse_time(x['event_endtime']  ), hek_times[-1]) )
        
        event_time = pandas.DateRange(event_starttime, event_endtime, offset = pandas.datetools.Second() )
        detected_times[x['frm_name']][event_time] = True
        detected_times[all_frms_name][event_time] = True
        detected_times[number_name][event_time] = detected_times[number_name][event_time] + 1.0

    return detected_times

def main():

    tstart = datetime.datetime(2011,3,5)
    tend = datetime.datetime(2011,3,6)

    result = hek_acquire(tstart, tend, directory = '~/Data/HEK/', verbose = True )

    detected_times = hek_detection_times(tstart, tend, result)

    detected_times['number'].plot()

    return detected_times

if __name__ == '__main__':
    main()
