"""
    Provides programs to process and analyze LYRA data. This module is
    currently in development.
   
    Examples
    --------
    To make a LYRA plot
    >>> import sunpy.instr.lyra as lyra
    >>> lobj = lyra.lyra()
    >>> lobj.download('2011/07/23')
    >>> lobj.load()
    >>> lobj.plot()
    
    To Do
    -----
    * An object should be developed to encapsulate all of goes functionality
    * LYRA FITS files store one day's of data at a time.  A simple extension
        of the code would make it easy download multiple days worth of data
        at the one time and create very large arrays of data between
        specific times.
    
    See Also
    --------
    For current data plots see http://proba2.sidc.be
    
    References
    ----------
    | http://proba2.sidc.be/index.html/science/lyra-analysis-manual/article/lyra-analysis-manual?menu=32

    """

import pyfits
import datetime
from matplotlib import pyplot as plt
import urllib,os
from sgmllib import SGMLParser
from sunpy.util.util import anytim

"""
class used to scrape the webpage
"""
class URLLister(SGMLParser):
        def reset(self):
                SGMLParser.reset(self)
                self.urls = []

        def start_a(self, attrs):
                href = [v for k, v in attrs if k=='href']
                if href:
                        self.urls.extend(href)

"""
Main LYRA object
"""
class lyra:
    def __init__(self):
        self.verbose = False
        self.filename = None
        self.data = None
        self.columns = None
        self.level = 2
        self.dataType = 'std'
        self.downloadto = os.path.expanduser('~')+os.sep
        self.location = 'http://proba2.oma.be/lyra/data/bsd/'
        self.prefix = 'lyra_'
        self.time = None
        
    def download(self,inputTime):
        """ Function to download LYRA data, and/or set the filename where it can be found"""

        self.time = anytim(inputTime)

        # date-based subdirectory
        dateLocation = self.time.strftime('%Y/%m/%d/')

        # date-based filename
        dateFilename = self.time.strftime('%Y%m%d-')

        # extension to the file name
        extension = '000000_lev'+ str(self.level) + '_' + self.dataType + '.fits'

        # calculated file name
        requestedLocation = self.location + dateLocation
        requestedFile  = self.prefix + dateFilename + extension

        f = os.path.expanduser(self.downloadto) + os.sep + requestedFile

        isAlreadyThere = os.path.isfile(f)

        if isAlreadyThere:
            if self.verbose:
                print('File '+ f + ' already exists.')
            self.filename = f
        else:
            self.filename = wgetDownload(requestedLocation,requestedFile, self.downloadto)

    def load(self):
        """Load the FITS file data into the object"""
        hdu = pyfits.open(self.filename)
        self.data = hdu[1].data
        self.columns = hdu[1].columns
        hdu.close()

    def plot(self):
        """Plot the LYRA data"""
        names = self.columns.names
        units = self.columns.units
        time = self.data.field(0)

        fig, axs = plt.subplots(4,1, sharex=True)

        for j in range(1,5):
            axs[j-1].plot(time,self.data.field(j))
            axs[j-1].set_ylabel( names[j] + ' (' + units[j] + ')' )

        plt.xlabel( names[0] + ' (' + units[0] + ')' )
        plt.show()

    def cut(self,time1,time2):
        """Returns a subsection of the data based on times"""
        pass

    def sumup(self,nbins):
        """Add up the data using a bin size in # bins"""
        n = self.data.field(0).size
        nNew = n/nbins
        dataNew = self.data
        for i in range(0,nNew):
            dataNew.field(0)[i] = data.field(0)[i*nNew]
        
        self.data = dataNew

#
# general purpose downloader using wget
#
def wgetDownload(requestedLocation,requestedFile, downloadto, verbose = False, overwrite=False):

    usock = urllib.urlopen(requestedLocation)
    parser = URLLister()
    parser.feed(usock.read())
    usock.close()
    parser.close()

    if verbose:
        print('Requested file = '+requestedFile)

    print(parser.urls)

    if not requestedFile in parser.urls:
        if verbose:
            print('Requested file not found.')
        return None
    else:
        if verbose:
            print('Downloading '+ requestedLocation+requestedFile)
        remoteBaseURL = '-B ' + requestedLocation + ' '
        localDir = ' -P'+downloadto + ' '
        command = 'wget -r -l1 -nd --no-parent ' + requestedLocation+requestedFile + localDir + remoteBaseURL
        if verbose:
            print('Executing '+command)
            print('File located at ' + downloadto + requestedFile)
        os.system(command)
        return downloadto + requestedFile

