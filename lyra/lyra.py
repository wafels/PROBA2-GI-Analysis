"""
Provides programs to process and analyze LYRA data. This module is
currently in development.

TODO
----
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
* Normalize download interface for LYRA, EVE, GOES, etc.
* Store units from hdulist
* Update header data when data is changed
* Test with partial data from current day
* When start or end dates are specified in the constructor truncate data in
  PyFITS before loading it into Lyra.

See Also
--------
* http://proba2.sidc.be

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
from matplotlib import pyplot as plt

class Lyra:
    """Simple class for working with PROBA2 LYRA data
    
    Parameters
    ----------
    input_ : string, pandas.core.frame.DataFrame
        Either a filepath to a Lyra FITS file to open, or a pandas DataFrame
        instance for such a file.
    header : pyfits.header.Header
        A PyFITS header instance. This is used when a new Lyra instance
        is created using an existing one.
    
    Attributes
    ----------
    data : pandas.core.frame.DataFrame
        A pandas DataFrame instance containing the LYRA data
    header : pyfits.header.Header
        A PyFITS header instance with the header tags associated with the LYRA
        data file.
        
    Examples
    --------
    >>> lyra = Lyra('lyra_20120320-000000_lev1_std.fits')
    >>> lyra.data['CHANNEL1']
    2012-03-20 00:00:00.090000    19.264077
    2012-03-20 00:00:00.140000    19.244072
    ...
    2012-03-20 23:59:59.939000    21.564563
    2012-03-20 23:59:59.989000    21.524555
    Name: CHANNEL1, Length: 1725538
    >>> lyra.data['CHANNEL1'].values
    array([ 19.264077,  19.244072,  19.204064, ...,  21.564563,  21.564563,
            21.524555])
    >>> lyra.discrete_boxcar_average().show()
    
    References
    ----------
    | http://proba2.oma.be/index.html/science/lyra-analysis-manual/article/lyra-analysis-manual?menu=32
    
    """
    def __init__(self, input_, header=None, start=None, end=None):
        """Lyra Constructor"""
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
            
        # Restrict data if request
        if start is not None or end is not None:
            self.data = self.truncate(start, end).data
            
    def load_file(self, filepath):
        """Loads LYRA data from a FITS file"""
        # Open file with PyFITS
        hdulist = pyfits.open(filepath)
        fits_record = hdulist[1].data

        # Start and end dates
        start_str = hdulist[0].header['date-obs']
        #end_str = hdulist[0].header['date-end']
        
        start = datetime.datetime.strptime(start_str, '%Y-%m-%dT%H:%M:%S.%f')
        #end = datetime.datetime.strptime(end_str, '%Y-%m-%dT%H:%M:%S.%f')

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
    
    def truncate(self, start=None, end=None):
        """Returns a truncated version of the Lyra object"""
        if start is None:
            start = self.data.index[0]
        if end is None:
            end = self.data.index[-1]
        
        truncated = self.data.truncate(sunpy.time.parse_time(start),
                                       sunpy.time.parse_time(end))
        return Lyra(truncated, self.header.copy())
        
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
    def download(self, date=None, directory="~", level=2, data_type='std'):
        """Downloads LYRA data associated with the specified time and saves it
        to the current working directory

        Parameters
        ----------
        date : datetime, string
            A datetime object or date string indicating the date for which
            date should be downloaded.
        directory : string
            The directory to save files to.
        level : int
            The processing level to download
        date_type : string
            The type of LYRA file to request. Currently only "std" supported.
            
        Returns
        -------
        out : Lyra
            A Lyra object instance for the file downloaded
        """
        dt = sunpy.time.parse_time(date or datetime.datetime.utcnow())

        # Filepath
        filename = "lyra_%s000000_lev%d_%s.fits" % (dt.strftime('%Y%m%d-'),
                                                    level, data_type)
        filepath = os.path.join(os.path.expanduser(directory), filename)
        
        # URL
        base_url = "http://proba2.oma.be/lyra/data/bsd/"
        url_path = urlparse.urljoin(dt.strftime('%Y/%m/%d/'), filename)
        url = urlparse.urljoin(base_url, url_path)

        # Save file
        print ("Downloading %s" % filename)
        
        try:            
            urllib.urlretrieve(url, filepath)
        except IOError:
            print("Error downloading %s. Is data available for that day?" % url)
            return

        return Lyra(filepath)
