from sunpy.net import hek
from sunpy.time import parse_time
from sunpy import lightcurve
from scipy import scipy.ndimage.label as label
import os
import datetime
import pickle
import pandas
import matplotlib.pyplot as plt

#
# Should really define an HEK interrogation object which has these methods
#
class fevent:
    """
    Feature and event interrogation object
    
    Simple interrogation of the HEK results.

    Parameters
    ----------
    args : filepath, url, or start and end dates
        The input for a LightCurve object should either be a filepath, a URL,
        or a date range to be queried for the particular instrument.

    Attributes
    ----------
    data : pandas.DataFrame
        An pandas DataFrame prepresenting one or more fields as they vary with 
        respect to time.
    header : string, dict
        The comment string or header associated with the light curve input

    Examples
    --------
    >>> import sunpy
    >>> import datetime
    >>> base = datetime.datetime.today()
    >>> dates = [base - datetime.timedelta(minutes=x) for x in 
    range(0, 24 * 60)]
    >>> light_curve = sunpy.lightcurve.LightCurve({"param1": range(24 * 60)}, 
    index=dates)
    >>> light_curve.show()

    References
    ----------
    | http://pandas.pydata.org/pandas-docs/dev/dsintro.html

    """
    def __init__(self, *args, **kwargs):
        self._filename = ""
        header = None


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
        hek_detections[frm] = 1
    hek_detections[all_frms_name] = 1
    hek_detections[number_name] = 1
    # Create the pandas dataframe
    detected_times = pandas.DataFrame(hek_detections, index = hek_times)

    # For each result get when it occurred. Classify by feature recognition method.
    for x in result:
        event_starttime = max( (parse_time(x['event_starttime']), hek_times[0]) )
        event_endtime =   min( (parse_time(x['event_endtime']  ), hek_times[-1]) )
        
        event_time = pandas.DateRange(event_starttime, event_endtime, offset = pandas.datetools.Second() )
        detected_times[x['frm_name']][event_time] = 1
        detected_times[all_frms_name][event_time] = 1
        detected_times[number_name][event_time] = detected_times[number_name][event_time] + 1

    return detected_times

def hek_split_timeline(timeline):
    """ Get the start and end times of all the events in a time line, and
    the start and end times of all the times when nothing happened """
    def hek_split_this(timeline):
        """Label all the individual events in a timeline, and return the
           start and end times """
        labels, numL = label(timeline)
        eventindices = [(labels == i).nonzero() for i in xrange(1, numL+1)]
        timeranges = []
        for event in eventindices:
            timeranges.append( timeline.index([event[0],event[-1]]) )
        return timeranges
    return hek_split_this(timeline), hek_split_this(1-timeline)


def main():

    tstart = datetime.datetime(2011,3,5)
    tend = datetime.datetime(2011,3,5,23,59,59)

    # acquire the HEK data
    result = hek_acquire(tstart, tend, directory = '~/Data/HEK/', verbose = True )

    # calculate the detection times from the event times
    detected_times = hek_detection_times(tstart, tend, result)
    
    # get the event label times, and the non-event label times
    eventtimes, noneventtimes = hek_split_timeline(detected_times["all_frms"])

    # acquire the LYRA data
    lyra = sunpy.lightcurve.LYRALightCurve(tstart)

    # subset the time-series for each event
    for event in eventtimes:
        this = lyra[event]
        # perform the necessary analysis on this event
        


    return detected_times

if __name__ == '__main__':
    main()
