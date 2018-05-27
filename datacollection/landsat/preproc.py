import os
import time
from os.path import exists, getsize
import h5py
import traceback
import MySQLdb as sql

from datacollection.landsat.dataImportUtils import PreProcStatus, purge_scene, metadataInsert
from datacollection.utils import ExceptionObj, generateFilePathStr
import datacollection.settings as settings
from datacollection.landsat.preprocH import *



############################# PREPROCESSOR CLASS #############################
class Preprocessor(object):
	def __init__(self):
		self.status = 'IDLE'
		self.sql_parameters = {
			'db': settings.DB,
			'host': settings.DB_HOST,
			'user': settings.DB_USER,
			'passwd': settings.DB_PASS
		}
		self.h5F = h5py.File(generateFilePathStr(kind='database'), 'a', libver='latest')


	def preproc(self, sceneid, status = None):
		if not os.path.exists(generateFilePathStr(sceneid, 'raw')):
			return(ExceptionObj('Scene not yet downloaded'))

		if status == None: self.status = PreProcStatus()
		else: self.status = status

		try:
			decomTar(
				generateFilePathStr(sceneid, 'raw', 'tar'),
				generateFilePathStr(sceneid, 'raw'),
				self.status
			)
			os.remove(generateFilePathStr(sceneid, 'raw', 'tar'))

			preProcObj = LandsatPreProcess(sceneid, self.h5F)
			preProcObj.compute()
			preProcObj.writeHDF_MAIN()
			self.status.updateProg()
			preProcObj.writeVis_MAIN()
			self.status.updateProg()

			db = sql.connect(**self.sql_parameters)
			cur = db.cursor()
			metadataInsert(sceneid, self.db, self.cur)
			cur.close()
			db.close()

			preProcObj.close()

		except:
			traceback.print_exc()
			purge_scene(sceneid, self.db, self.cur, self.h5F)
			return(ExceptionObj('preprocessing failed'))

		return(0)
