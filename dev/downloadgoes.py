
import pandas
import urllib2
from matplotlib import pyplot as plt
csv = urllib2.urlopen('http://www.ngdc.noaa.gov/goes/sem/getData/goes15/xrs_2s.csv?fromDate=20111220&toDate=20111221')
ts = pandas.read_csv(csv, index_col=0, parse_dates=True)
ts.plot()
plt.show()
