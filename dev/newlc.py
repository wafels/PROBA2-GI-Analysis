import sunpy
lyra = sunpy.lightcurve.LYRALightCurve('2011/04/01', directory = '~/Data/PROBA2/LYRA/fits/')
lyra.show()