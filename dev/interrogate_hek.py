from sunpy.net import hek
from sunpy.time import parse_time
from sunpy.time.timerange import TimeRange
from sunpy.lightcurve import LogicalLightCurve
from sunpy.lightcurve import LYRALightCurve
from sunpy.lightcurve import LightCurve
import numpy as np
import os
import datetime
import pickle
import pandas

from proba2gi2 import EventTimeRange

class fevent:
    """
    Feature and event interrogation object. Simple interrogation of the HEK
    results.
    """
    def __init__(self, tstart, tend=None, event_type='FL', extension=None,
                 directory='~', verbose=False, filename=None):
        """acquire HEK results from file, or download and save them"""
        
        # define the start and end times of the query
        self.tstart = parse_time(tstart)
        if tend is None:
            self.tend = self.tstart + \
            datetime.timedelta(days=1)
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
            self.filename = self.tstart.strftime("%Y%m%d_%H%M%S") + '__' + \
            self.tend.strftime("%Y%m%d_%H%M%S") + \
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
            pickle.dump(self.result, open( self.filepath, "wb" ))
            
    def count(self, frm_name='combine', tstart=None, tend=None):
        """Since the same event can be counted by many different algorithms, it
        is interesting to count the number of detections as a function of
        time in a given time range"""
        # Create the pandas time series
        index = pandas.date_range(self.tstart, self.tend, freq = 'S')
        time_series = pandas.Series(np.zeros(len(index)), dtype=bool,
                                    index = index)
        return LightCurve(time_series,header = {"event_type":self.event_type,
                                                  "frm_name":frm_name})


    def onoff(self, frm_name='combine', tstart=None, tend=None, 
              operator = ['>=','<=','and']):
        """Return a Logical lightcurve object.  The duration of the event is 
        indicated with the value 'True', and all other values are indicated 
        with a 'False'.  This is calculated within the range tstart and tend.
        """
        
        # Get the event start and end times
        result = self.times(frm_name=frm_name, tstart=tstart, tend=tend, operator=operator)

        # Create the pandas time series
        index = pandas.date_range(self.tstart, self.tend, freq = 'S')
        time_series = pandas.Series(np.zeros(len(index)), dtype=bool,
                                    index = index)

        # Go through each result and get the start and end times
        for timerange in result:
            time_series[timerange.start():timerange.end()] = True
        return LogicalLightCurve.create(time_series,
                                        header = {"event_type":self.event_type,
                                                  "frm_name":frm_name})
    
    def times(self, frm_name='combine', tstart=None, tend=None, 
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
        frms = list( set( [ x['frm_name'] for x in self.result ] ) )
        if not(frm_name in frms) and frm_name != 'combine':
            print('frm_name not recognised')
            return None
        
        # define the index
        index = pandas.date_range(self.tstart, self.tend, freq = 'S')

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
            
            if eval('lo_logic ' + operator[2] + ' hi_logic'):
                if x['frm_name'] == frm_name:
                    events.append( EventTimeRange(event_starttime, event_endtime) )
                elif frm_name == 'combine':
                    events.append( EventTimeRange(event_starttime, event_endtime) )
        return events
