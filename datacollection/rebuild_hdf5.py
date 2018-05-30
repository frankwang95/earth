import os
import h5py
import MySQLdb as sql

import datacollection.settings as settings
from datacollection.utils import generateFilePathStr
from datacollection.landsat.preprocH import LandsatPreProcess
from datacollection.landsat.dataImportUtils import cleanup

def rebuild_hdf5():
	print("Regenerating HDF5 file...")
	# Get lids from image index
	db = sql.connect(
		db=settings.DB,
		host=settings.DB_HOST,
		user=settings.DB_USER,
		password=settings.DB_PASS
	)
	cur = db.cursor()
	cur.execute('SELECT lid FROM imageindex')
	lids = [r[0] for r in cur.fetchall()]
	cur.close()
	db.close()
	print("Found {} scenes to add".format(len(lids)))

	# Create new HDF5 database removing old one if needed
	if os.path.isfile(generateFilePathStr(kind='database')):
		os.remove(generateFilePathStr(kind='database'))
	h5F = h5py.File(generateFilePathStr(kind='database'), 'a', libver='latest')

	# Use PreProcH to reinsert all items from raw images
	print
	for i in range(len(lids)):
		print('\rInserting {}/{}'.format(i, len(lids)), end='')
		preprocessor = LandsatPreProcess(lids[i], h5F)
		preprocessor.writeHDF_MAIN()
	print

	# Cleanup and close resources
	# SQL resources are restarted to prevent timeouts during long rebuilds
	db = sql.connect(
		db=settings.DB,
		host=settings.DB_HOST,
		user=settings.DB_USER,
		password=settings.DB_PASS
	)
	cur = db.cursor()
	cleanup(db, cur, h5F)
	cur.close()
	db.close()
	h5F.close()

rebuild_hdf5()
