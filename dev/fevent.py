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

    """
    def __init__(self, tstart, tend=None, event_type='FL', extension=None,
                 directory='~', verbose=False, filename=None):
        """acquire HEK results from file, or download and save them"""
        
        # define the start and end times of the query
        self.tstart = parse_time(tstart)
        if tend is None:
            self.tend = self.tstart + datetime.timedelta(days=1)
        else:
            self.tend = parse_time(tend)
         
        # event type
        self.event_type = event_type
  
        # extension
        if extension is None:
            self.extension = '.hek.' + self.event_type + '.pickle'
        else:
            self.extension = extension
        
        # directory
        self.directory = directory
   
        # create a filename if none passed
        if filename is None:
            self.filename = self.tstart.strftime("%Y%m%d_%H%M%S") + '__' + 
            self.tend.strftime("%Y%m%d_%H%M%S") + 
            self.extension

        # get the full file path
        self.filepath = os.path.join(os.path.expanduser(self.directory), 
                                     self.filename)
    
        # either load the data or go get it
        if os.path.isfile(self.filepath):
            if verbose:
                print('Loading local file: ' + self.filepath)
            self.result = pickle.load(open( self.filepath, "rb" ) )
        else:
            if verbose:
                print('Querying HEK for data and will save to following file: '+
                       self.filepath)

            client = hek.HEKClient()
            self.result = client.query(hek.attrs.Time(self.tstart,self.tend), 
                                  hek.attrs.EventType(self.event_type))
            pickle.dump(result, open( self.filepath, "wb" ))

    def onoff(self, frm_name='all', tstart=None, tend=None, 
              operator = ['>=','<=','and']):
        """Return a single pandas timeseries that indicates when all the
        events within tstart and tend have occurred.  The duration of the
        event is indicated by the value 1."""
        
        # Get the event start and end times
        result = self.times(frm_name=frm_name, tstart=tstart, tend=tend, 
                            operator=operator)

        # Create the pandas time series
        index = pandas.DateRange(self.tstart, self.tend, 
                                 offset=pandas.datetools.Second() )
        time_series = pandas.Series(1, index = index)
       
        # Go through each result and get the start and end times
        for x in result:
            time_series[ pandas.DateRange(x[0], x[1], offset = 
                                          pandas.datetools.Second())] = 1
        return time_series
    
    def times(self, frm_name='all', tstart=None, tend=None, 
              operator = ['>=','<=','and']):
        """Return a list of start and end times within the requested time range
        with the correct logic on the event time comparison"""

        # Parse and check the input times
        if tstart is None:
            tstart = parse_time(self.tstart)
        else:
            tstart = parse_time(tstart)
        if tend is None:
            tend = parse_time(self.tend)
        else:
            tend = parse_time(tend)
        if tstart > tend:
            print('Start time is larger than the end time')
            return None

        # Get and check the unique feature recognition methods
        frms = list( set( [ x['frm_name'] for x in result ] ) )
        if not(frm_name in frms) and frm_name != 'all':
            print('frm_name not recognised')
            return None

        # Limits to the times
        lo_limit = max( (index[0],tstart) )
        hi_limit = min( (index[-1],tend) )

        # Go through each result and get the start and end times
        events = []
        for x in self.result:
            event_starttime = parse_time(x['event_starttime'])
            event_endtime = parse_time(x['event_endtime'])
            
            # implement the requested comparison of the event times with
            # the limit of the extent of the time range
            if operator[0] == 'None':
                lo_logic = None
            else:
                lo_logic = eval('event_starttime' + operator[0] + 'lo_limit')
            if operator[1] == 'None':
                hi_logic = None
            else:
                hi_logic = eval('event_endtime' + operator[1] + 'hi_limit')
            
            if eval('lo_logic' + operator[2] + 'hi_logic')
                if x['frm_name'] == frm_name:
                    events = events[(event_starttime, event_endtime)]
                elif frm_name == 'all':
                    events = events[(event_starttime, event_endtime)]
        return events


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

    tstart = '2011/03/05'

    # acquire the HEK data
    result = fevent(tstart, directory='~/Data/HEK/', verbose=True)
    
    # get a lightcurve of when an event was detected
    detected = fevent.onoff()
    
    # get a lightcurve of when an event was not detected
    no_detection = 1 - detected

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
