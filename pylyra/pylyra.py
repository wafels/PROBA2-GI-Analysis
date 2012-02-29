
import pyfits
import datetime
from matplotlib import pyplot as plt
import urllib,os
from sgmllib import SGMLParser

class lyra:
    def __init__(self):
        self.verbose = False

    def download(self,inputTime, level = 2, dataType = 'std', downloadto = '/Users/ireland/PROBA2_GI/dat/fits/'):
        """ Function to download LYRA data"""

        # location of the data on the web
        location = 'http://proba2.oma.be/lyra/data/bsd/'
        # prefix to the FITS file
        prefix = 'lyra_'
        # date-based subdirectory
        dateLocation = inputTime.strftime('%Y/%m/%d/')
        # date-based filename
        dateFilename = inputTime.strftime('%Y%m%d-')
        # extension to the file name
        extension = '000000_lev'+ str(level) + '_' + dataType + '.fits'
        # calculated file name
        requestedLocation = location + dateLocation
        requestedFile  = prefix+dateFilename + extension

        isAlreadyThere = os.path.isfile(os.path.expanduser(downloadto + requestedFile))

        if isAlreadyThere:
            if verbose:
                print('File '+downloadto + requestedFile + ' already exists.')
            return os.path.expanduser(downloadto + requestedFile)
        else:
            return wgetDownload(requestedLocation,requestedFile, downloadto, verbose = verbose)



class URLLister(SGMLParser):
        def reset(self):
                SGMLParser.reset(self)
                self.urls = []

        def start_a(self, attrs):
                href = [v for k, v in attrs if k=='href']
                if href:
                        self.urls.extend(href)


#
# Simple function to acquire LYRA data
#
def getData(inputTime, level = 2, dataType = 'std', downloadto = '/Users/ireland/PROBA2_GI/dat/fits/', verbose = False):

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

def load(filename):
    hdu = pyfits.open(filename)
    hdu.close()
    return hdu


def summary(hdu, hours = False, all = True):

    # get the data
    tbdata = hdu[1].data

    # get the column information
    cols = hdu[1].columns

    # Get the names of the columns
    names = cols.names

    # Get the units of the columns
    units = cols.units

    time = tbdata.field(0)
    if hours:
        # Convert time to hours
        time = time/3600.0
        units[0] = 'hours'

    if all:
        fig, axs = plt.subplots(4,1, sharex=True)
        #plt.subplots_adjust(hspace=0.001)
        for j in range(1,5):
            axs[j-1].plot(time,tbdata.field(j))
            axs[j-1].set_ylabel( names[j] + ' (' + units[j] + ')' )

        plt.xlabel( names[0] + ' (' + units[0] + ')' )
        plt.show()


