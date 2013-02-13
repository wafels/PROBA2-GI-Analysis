import sunpy
from sunpy.net.helioviewer import HelioviewerClient
hv = HelioviewerClient()
f171 = hv.download_jp2('2012/07/05 00:30:00', observatory='SDO', instrument='AIA', detector='AIA', measurement='171')
mhv171 = sunpy.map.make_map(f171)

#goes = sunpy.lightcurve.GOESLightCurve.create('2012/06/01', '2012/06/05')
#goes = sunpy.lightcurve.GOESLightCurve.create('2012/06/01', '2012/06/05')
