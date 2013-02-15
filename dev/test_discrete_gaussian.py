# Read in a CSV file corresponding to a LYRA time-series, and
# create a distribution with the same properties.
import csv
import numpy as np

def main():

    # location of the LYRA CSV data
    directory = ''
    filename = ''

    # read in the LYRA CSV file
    f = open(directory+filename,'rb')
    lyra = csv.reader(f)
    f.close()

    # Get the second column as a numpy array
    data = np.array(lyra???)

    # form the normalized histogram.  make sure the bins are small enough to
    # grab 
    h = (np.histogram(data, bins=10))
    

    # Create some data which have the same distribution as the histogram
    for i in range(0,n):
        r 
    
    # Write this out to another CSV file that will be read in by R and analyzed using the fArma package.

  
    return tsnew
 
if __name__ == '__main__':
    main()