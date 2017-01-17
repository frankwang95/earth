from os.path import exists, getsize
import os
import sys
import MySQLdb as sql
import h5py

sys.path.insert(0,'..')
from dataImportUtils import PreProcStatus
from utils import ExceptionObj, generateFilePathStr
import settings
from preprocH import *



############################### METADATA PARSER #############################
def metadataInsert(sceneid, db, cur):
	h = open(generateFilePathStr(sceneid, 'raw', 'metadata'), 'r')
	rawMetaData = h.readlines()
	h.close()

	splitTags = [i.strip().split(' = ') for i in rawMetaData]
	splitTags = {x[0]:x[1] for x in splitTags if len(x) >= 2}

	time = splitTags['DATE_ACQUIRED'] + ' ' + splitTags['SCENE_CENTER_TIME'][1:9]
	ul_lat = splitTags['CORNER_UL_LAT_PRODUCT']
	ul_lon = splitTags['CORNER_UL_LON_PRODUCT']
	ur_lat = splitTags['CORNER_UR_LAT_PRODUCT']
	ur_lon = splitTags['CORNER_UR_LON_PRODUCT']
	ll_lat = splitTags['CORNER_LL_LAT_PRODUCT']
	ll_lon = splitTags['CORNER_LL_LON_PRODUCT']
	lr_lat = splitTags['CORNER_LR_LAT_PRODUCT']
	lr_lon = splitTags['CORNER_LR_LON_PRODUCT']
	ul_proj_x = splitTags['CORNER_UL_PROJECTION_X_PRODUCT']
	ul_proj_y = splitTags['CORNER_UL_PROJECTION_Y_PRODUCT']
	ur_proj_x = splitTags['CORNER_UR_PROJECTION_X_PRODUCT']
	ur_proj_y = splitTags['CORNER_UR_PROJECTION_Y_PRODUCT']
	ll_proj_x = splitTags['CORNER_LL_PROJECTION_X_PRODUCT']
	ll_proj_y = splitTags['CORNER_LL_PROJECTION_Y_PRODUCT']
	lr_proj_x = splitTags['CORNER_LR_PROJECTION_X_PRODUCT']
	lr_proj_y = splitTags['CORNER_LR_PROJECTION_Y_PRODUCT']
	cloud_cover = splitTags['CLOUD_COVER']
	roll_angle = splitTags['ROLL_ANGLE']
	sun_azimuth = splitTags['SUN_AZIMUTH']
	sun_elev = splitTags['SUN_ELEVATION']
	earth_sun_dist = splitTags['EARTH_SUN_DISTANCE']
	orientation = splitTags['ORIENTATION']

	enterCmd = u'''INSERT INTO imageindex VALUES ('{0}', '{1}', {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23});'''.format(
		sceneid,
		time,
		ul_lat,
		ul_lon,
		ur_lat,
		ur_lon,
		ll_lat,
		ll_lon,
		lr_lat,
		lr_lon,
		ul_proj_x,
		ul_proj_y,
		ur_proj_x,
		ur_proj_y,
		ll_proj_x,
		ll_proj_y,
		lr_proj_x,
		lr_proj_y,
		cloud_cover,
		roll_angle,
		sun_azimuth,
		sun_elev,
		earth_sun_dist,
		orientation
	)

	cur.execute(enterCmd)
	db.commit()
	return(0)



############################### PREPROCESSOR CLASS #############################
class Preprocessor(object):
	def __init__(self):
		self.status = 'IDLE'

		self.db = sql.connect(
			db="earthdat",
			host=settings.DB_HOST,
			user=settings.DB_USER,
			passwd=settings.DB_PASS
		)
		self.cur = self.db.cursor()

		self.h5F = h5py.File(generateFilePathStr(type = 'database'), 'w')


	def preproc(self, sceneid, status = None):
		if not os.path.exists(generateFilePathStr(sceneid, 'raw')):
			return(ExceptionObj('Scene not yet downloaded'))

		if status == None: self.status = PreProcStatus()
		else: self.status = status

		# decompress
		try:
			decomTar(
				generateFilePathStr(sceneid, 'raw', 'tar'),
				generateFilePathStr(sceneid, 'raw'),
				self.status
			)
			os.remove(generateFilePathStr(sceneid, 'raw', 'tar'))


		except:
			for i in os.listdir(generateFilePathStr(sceneid, 'raw')):
				os.remove(generateFilePathStr(sceneid, 'raw', i))
			os.rmdir(generateFilePathStr(sceneid, 'raw'))
			return(ExceptionObj('extraction failed'))

		# preprocess
		preProcObj = LandsatPreProcess(sceneid, self.h5F)
		preProcObj.compute()
		preProcObj.writeHDF_MAIN()
		self.status.updateProg()
		preProcObj.writeVis_MAIN()
		self.status.updateProg()

		print metadataInsert(sceneid, self.db, self.cur)
		
		preProcObj.close()
		return(0)


	def shutdown(self):
		self.h5F.close()
		self.cur.close()
		self.db.close()
		return(0)
