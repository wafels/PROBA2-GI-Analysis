import pylyra2
import datetime

# initiate the object
lobj = pylyra2.lyra()

# load the data into the hdu
lobj.download('2011/06/29')

# plot the summary
lobj.plot()
