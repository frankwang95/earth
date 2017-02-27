from os.path import exists, getsize
import os
import sys
import MySQLdb as sql
import h5py

sys.path.insert(0,'..')
from dataImportUtils import PreProcStatus, remove_scene, metadataInsert
from utils import ExceptionObj, generateFilePathStr
import settings
from preprocH import *



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

		self.h5F = h5py.File(generateFilePathStr(type = 'database'), 'a')


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

		except:
			self.clean(sceneid)
			return(ExceptionObj('preprocing failed'))
		
		return(0)


	def clean(self, sceneid):
			try:
				for i in os.listdir(generateFilePathStr(sceneid, 'raw')):
					os.remove(generateFilePathStr(sceneid, 'raw', i))
			except: pass

			try: os.rmdir(generateFilePathStr(sceneid, 'raw'))
			except: pass
			
			try: os.remove(generateFilePathStr(sceneid, 'preproc', 'visible'))
			except: pass

			try: remove_scene(sceneid, self.db, self.cur)
			except: pass

			try: del self.h5F[sceneid]
			except: pass


	def shutdown(self):
		self.h5F.close()
		self.cur.close()
		self.db.close()
		return(0)
