import pylyra2
import datetime

# set up the data you want
date = datetime.datetime(2011,03,04)

# initiate the object
lobj = pylyra2.lyra()

# download the data
lobj.download(date)

# load the data into the hdu
lobj.load()

# plot the summary
lobj.plot()

# sum the data
lobj.sumup(
