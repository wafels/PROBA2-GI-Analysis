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
from sunpy.time.util import TimeRange

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

        # define the start and end times 
        self.tstart = self.time
        self.tend = self.time + datetime.timedelta(seconds = self.data.field(0)[-1])

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


def sub(lyra,t1,t2):
    """Returns a subsection of LYRA based on times
         which is also a LYRA object."""
    tr = TimeRange(t1,t2)
    if tr.t1 < lyra.tstart:
        print('Requested start time less than data start time.')
        indexStart = 0
    else:
        indexStart = getLyraIndexGivenTime(lyra.time,lyra.data.field(0), t1)
        lyra.tstart = getLyraTimeGivenIndex(lyra,indexStart)
    if tr.t2 > lyra.tend:
        print('Requested end time greater than data start time.')
        indexEnd = lyra.time.size-1
    else:
        indexEnd = getLyraIndexGivenTime(lyra.time,lyra.data.field(0), t2)
        lyra.tend = getLyraTimeGivenIndex(lyra,index)

    lyra.data = data.field(:)[:,indexStart:indexEnd]
    return lyra


def getLyraTimeGivenIndex(lyra,index):
    """Given an index, return a time from the LYRA sample times"""
    return lyra.time + datetime.timedelta(seconds = lyra.data.field(0)[index])

def getLyraIndexGivenTime(lyra,targetTime):
    """Given a target time, return an index based on the LYRA sample times"""
    earlyIndex = 0
    lateIndex = lyra.time.size-1
    previousIndex = 0
    while (midIndex != previousIndex):
        midIndex = 0.5*(earlyIndex + lateIndex)
        tmidpoint = getLyraTimeGivenIndex(lyra,midIndex)
        if targetTime >= tmidpoint:
            earlyIndex = midIndex
            previousIndex = midIndex
        if targetTime < tmidpoint
            lateIndex = midIndex
            previousIndex = midIndex
    return midIndex



def sumup(self,nbins):
    """Add up the data using a bin size in # bins"""
    n = self.data.field(0).size
    nNew = n/nbins
    dataNew = self.data
    for i in range(0,nNew):
        dataNew.field(0)[i] = data.field(0)[i*nNew]
    self.data = dataNew
