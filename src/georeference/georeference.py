from osgeo import gdal
from osgeo import osr
import numpy as np
from functools import partial



def lonLatF(gt, ct, h, m) :
	ulon = point[0]*gt[1]+gt[0]
	ulat = point[1]*gt[5]+gt[3]
	(lon,lat,holder) = ct.TransformPoint(ulon,ulat)
	return((lon, lat))


def latLonToPixel(geotifAddr, latLonPairs):
	ds = gdal.Open(geotifAddr)
	gt = ds.GetGeoTransform()
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srsLatLong,srs)
	pixelPairs = []
	for point in latLonPairs:
		(point[1],point[0],holder) = ct.TransformPoint(point[1],point[0])
		x = (point[1]-gt[0])/gt[1]
		y = (point[0]-gt[3])/gt[5]
		pixelPairs.append([int(x),int(y)])
	return pixelPairs


def pixelToLatLon(geotifAddr, h, w):
	ds = gdal.Open(geotifAddr)
	gt = ds.GetGeoTransform()
	srs = osr.SpatialReference()
	srs.ImportFromWkt(ds.GetProjection())
	srsLatLong = srs.CloneGeogCS()
	ct = osr.CoordinateTransformation(srs, srsLatLong)

	lonLatPairs = ""
	for point in [[i, j] for i in range(h) for j in range(w)]:
		print (i, j)
		ulon = point[0]*gt[1]+gt[0]
		ulat = point[1]*gt[5]+gt[3]
		(lon,lat,holder) = ct.TransformPoint(ulon,ulat)
		lonLatPairs += str(lon) + str(lat) + "\n"

	h.open('test')
	h.write(lonLatPairs)
	h.close()
	return latLonPairs