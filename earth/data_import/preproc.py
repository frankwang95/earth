import os
from os.path import exists, getsize
import h5py
import MySQLdb as sql

from earth.data_import.dataImportUtils import PreProcStatus, purge_scene, metadataInsert
from earth.utils import ExceptionObj, generateFilePathStr
import earth.settings as settings
from earth.data_import.preprocH import *



############################### PREPROCESSOR CLASS #############################
class Preprocessor(object):
	def __init__(self):
		self.status = 'IDLE'

		self.db = sql.connect(
			db=settings.DB,
			host=settings.DB_HOST,
			user=settings.DB_USER,
			passwd=settings.DB_PASS
		)
		self.cur = self.db.cursor()

		self.h5F = h5py.File(generateFilePathStr(kind = 'database'), 'a')


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

			metadataInsert(sceneid, self.db, self.cur)
			preProcObj.close()

		except Exception as e:
			purge_scene(sceneid, self.db, self.cur, self.h5F)
			return(ExceptionObj('preprocing failed'))

		return(0)
