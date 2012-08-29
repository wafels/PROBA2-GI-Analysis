import sunpy
goes = sunpy.lightcurve.GOESLightCurve('2011/05/12','2011/05/13')
goes.show()
lyra = sunpy.lightcurve.LYRALightCurve('http://proba2.oma.be/lyra/data/bsd/2011/05/12/lyra_20110512-000000_lev2_std.fits')
lyra.show()