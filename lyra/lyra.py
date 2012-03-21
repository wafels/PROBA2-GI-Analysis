"""
Provides programs to process and analyze LYRA data. This module is
currently in development.

Examples
--------
In [1]: lyra = Lyra('lyra_20120320-000000_lev1_std.fits')
In [2]: lyra.discrete_boxcar_average().show()
In [3]: lyra.data['CHANNEL1']
Out[3]: 
2012-03-20 00:00:00.090000    19.264077
2012-03-20 00:00:00.140000    19.244072
...
2012-03-20 23:59:59.939000    21.564563
2012-03-20 23:59:59.989000    21.524555
Name: CHANNEL1, Length: 1725538
In [4]: lyra.data['CHANNEL1'].values
Out[4]: 
array([ 19.264077,  19.244072,  19.204064, ...,  21.564563,  21.564563,
        21.524555])

To Do
-----
* An object should be developed to encapsulate all of LYRA functionality
* LYRA FITS files store one day's of data at a time.  A simple extension
    of the code would make it easy download multiple days worth of data
    at the one time and create very large arrays of data between
    specific times.
* Add method to select a sub-region of FITS data to use before building
  pandas DataFrame, or afterwards using DataFrame.truncate(start_date, end_date)
* Create a generalized sunpy.TimeSeries object based on Lyra object below
  and inherit from that object (may be better to have sunpy.TimeSeries inherit
  from panda.TimeSeries or DataFrame first though).
* Store units from hdulist

See Also
--------
For current data plots see http://proba2.sidc.be

References
----------
| http://proba2.sidc.be/index.html/science/lyra-analysis-manual/article/lyra-analysis-manual?menu=32

"""
import os
import sys
import urllib
import urlparse
import datetime
import pyfits
import pandas
import sunpy
import numpy as np
from matplotlib import pyplot as plt

class Lyra:
    """Simple class for working with PROBA2 LYRA data"""
    def __init__(self, input_, header=None):
        """Create a new Lyra object instance"""
        # DataFrame + Header
        if (isinstance(input_, pandas.core.frame.DataFrame) and 
            isinstance(header, pyfits.header.Header)):
            self.data = input_
            self.header = header           
        # Filepath
        elif isinstance(input_, basestring):
            # Filepath
            if os.path.isfile(input_):
                self.load_file(input_)
            else:
                print "Invalid filepath specified."
                sys.exit()
        # Other
        else:
            print "Unsupported input specified"""
            sys.exit()
            
    def load_file(self, filepath):
        """Loads LYRA data from a FITS file"""
        # Open file with PyFITS
        hdulist = pyfits.open(filepath)
        fits_record = hdulist[1].data

        # Start and end dates
        start_str = hdulist[0].header['date-obs']
        end_str = hdulist[0].header['date-end']
        
        start = datetime.datetime.strptime(start_str, '%Y-%m-%dT%H:%M:%S.%f')
        end = datetime.datetime.strptime(end_str, '%Y-%m-%dT%H:%M:%S.%f')

        # First column are times
        times = [start + datetime.timedelta(0, n) for n in fits_record.field(0)]

        # Rest of columns are the data
        table = {}

        for i, col in enumerate(fits_record.columns[1:-1]):
            table[col.name] = fits_record.field(i + 1)
            
        # Create a Pandas DataFrame object
        self.data = pandas.DataFrame(table, index=times)
        self.header = hdulist[0].header
        
        
    def discrete_boxcar_average(self, seconds=1):
        """Computes a discrete boxcar average for the DataFrame"""
        date_range = pandas.DateRange(self.data.index[0], self.data.index[-1], 
                                      offset=pandas.datetools.Second(seconds))
        grouped = self.data.groupby(date_range.asof)
        subsampled = grouped.mean()
        
        return Lyra(subsampled, self.header.copy())
        
    def show(self):
        """Plots the LYRA data
        
        See: http://pandas.sourceforge.net/visualization.html
        """
        axes = self.data.plot(subplots=True, sharex=True)       
        plt.legend(loc='best')
        
        for i, name in enumerate(self.data.columns):
            axes[i].set_ylabel("%s (%s" % (name, "UNITS"))
            
        axes[0].set_title("LYRA")
        axes[-1].set_xlabel("Time")
        plt.show()
        
    @classmethod
    def download(self, date, level=2, data_type='std'):
        """Downloads LYRA data associated with the specified time and saves it
        to the current working directory"""
        dt = sunpy.time.parse_time(date)

        # Filepath
        filename = "lyra_%s000000_lev%d_%s.fits" % (dt.strftime('%Y%m%d-'),
                                                    level, data_type)
        filepath = os.path.join(os.path.expanduser("~"), filename)
        
        # URL
        base_url = "http://proba2.oma.be/lyra/data/bsd/"
        url = urlparse.urljoin(base_url, dt.strftime('%Y/%m/%d/'), filename)

        # Save file
        urllib.urlretrieve(url, filepath)        
