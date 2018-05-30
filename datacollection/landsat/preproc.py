import os
import time
from os.path import exists, getsize
import h5py
import MySQLdb as sql

from datacollection.landsat.dataImportUtils import PreProcStatus, purge_scene, metadataInsert
from datacollection.utils import generateFilePathStr
import datacollection.settings as settings
from datacollection.landsat.preprocH import *



############################# PREPROCESSOR CLASS #############################
class Preprocessor(object):
	def __init__(self, logger):
		self.status = 'IDLE'
		self.logger = logger
		self.sql_parameters = {
			'db': settings.DB,
			'host': settings.DB_HOST,
			'user': settings.DB_USER,
			'passwd': settings.DB_PASS
		}
		self.h5F = h5py.File(generateFilePathStr(kind='database'), 'a', libver='latest')


	def preproc(self, sceneid, status = None):
		if not os.path.exists(generateFilePathStr(sceneid, 'raw')):
			self.logger.warning('scene {} not yet downloaded'.format(sceneid))

		if status is None: self.status = PreProcStatus()
		else: self.status = status

		db = sql.connect(**self.sql_parameters)
		cur = db.cursor()

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

			metadataInsert(sceneid, db, cur)
			preProcObj.close()

		except:
			self.logger.exception('problem encountered while preprocessing scene: {}'.format(sceneid))
			self.logger.info('attempting to cleanup after preprocessing failure in scene {}'.format(sceneid))
			purge_scene(sceneid, db, cur, self.h5F)

		cur.close()
		db.close()
		self.logger.info('scene {} successfully processed'.format(sceneid))
