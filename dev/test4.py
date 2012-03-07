import pylyra2

# initiate the object
lyra = pylyra2.lyra()

# load the data into the hdu
lyra.download('2011/06/29')

# get a subsection
subsection = pylyra2.sub(lyra,'2011/06/29',400)

# plot the summary of the sub-section
subsection.plot()
