import pylyra
import pyfits
import datetime
import numpy as np
from matplotlib import pyplot as plt

# set up the data you want
date = datetime.datetime(2011,03,04)

# acquire the data
filename = pylyra.getData(date,verbose=True)

# load it in
lyraData = pylyra.load(filename)

# Sum the data
lyraData = pylyra.sum(lyraData,)

# cut the data down
lyraData = pylyra.cut(lyraData,dateStart,dateEnd)


hdu = pyfits.open(filename)

# get the data
tbdata = hdu[1].data

# get the column information
cols = hdu[1].columns

# Get the names of the columns
names = cols.names

# Get the units of the columns
units = cols.units

hdu.close()

def cut(lyraData, dateStart,dateEnd):
    

def sss(d,nSum):
    nd = d.size
    nNew = nd / 2
    dNew = np.zeros()
    for i in range(0,nd):
        dNew[i] = a[i*nSum, i*(nSum)-1]
    return dNew
    

#pylyra.summary(filename)
