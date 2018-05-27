import threading
import random
import shutil
import time
import os
import sys
from calendar import monthrange
import MySQLdb as sql
import logging

import datacollection.landsat.download as download
import datacollection.landsat.preproc as preproc
from datacollection.landsat.dataImportUtils import(
	check_scene_exists,
	DownloadStatus,
	PreProcStatus,
	cleanup,
	random_date
)
import datacollection.settings as settings
from datacollection.utils import (
	check_create_folder,
	generateFilePathStr
)


class Task:
	def __init__(self, id):
		self.id = id
		self.status = 'PENDING'
		self.history = []

	def updateStatus(self, obj):
		self.history.append(self.status)
		self.status = obj
		return(0)


class Scheduler:
	def __init__(self):
		#check-installation
		check_create_folder(generateFilePathStr())
		check_create_folder(generateFilePathStr(kind='raw'))
		check_create_folder(generateFilePathStr(kind='preproc'))
		check_create_folder(generateFilePathStr(kind='preproc', file='visible'))
		check_create_folder('logs')

		self.log_name = str(int(time.time())) + '.log'
		self.logger = logging.getLogger('data_import')
		self.logger.setLevel(logging.INFO)
		handler = logging.FileHandler('logs/{}'.format(self.log_name))
		handler.setFormatter(logging.Formatter(
		    '[%(asctime)s] [%(levelname)s] %(message)s',
		    '%Y:%m:%d-%H:%M:%S'
		))
		self.logger.addHandler(handler)

		#initialize
		self.pausedT = False
		self.pausedDownloadT = False
		self.pausedPreprocT = False
		self.shutdownT = False
		self.shutdownDownloadT = False
		self.shutdownPreprocT = False

		self.db = sql.connect(
			db=settings.DB,
			host=settings.DB_HOST,
			user=settings.DB_USER,
			passwd=settings.DB_PASS
		)
		self.cur = self.db.cursor()
		self.cur.execute('SET SESSION wait_timeout=31536000;')

		self.d = download.Downloader()
		self.p = preproc.Preprocessor()

		self.d_queue_auto = []
		self.d_queue_man = []
		self.p_queue = []
		self.addScenes()

		self.logger.info('scheduler started')
		threading.Thread(target=self.downloadHandler).start()
		threading.Thread(target=self.preprocHandler).start()
		threading.Thread(target=self.shutdownHandler).start()


	def addScenes(self):
		self.logger.info('adding available scenes to queue')
		with open(os.path.join(
			sys.prefix, 'lib', 'python3.6', 'site-packages', 'earth',
			'data_import', 'landsat', 'available_scenes'
		), 'r') as f: available_scenes = f.readlines()
		random.shuffle(available_scenes)
		self.d_queue_auto = [Task(scene[:-1]) for scene in available_scenes]
		self.logger.info('queue updated with all available scenes')


	def insertJob(self, sceneid):
		if not check_scene_exists(sceneid, self.db, self.cur):
			self.d_queue_man.append(Task(sceneid))
			self.logger.info('scene {0} inserted into manual queue'.format(sceneid))
			return(0)
		self.logger.info('scene {0} already in image index'.format(sceneid))
		return(1)


	def downloadHelper(self, x):
		if check_scene_exists(x.id, self.db, self.cur):
			self.logger.info('scene {0} already in index, continuing'.format(x.id))
			return(0)

		x.updateStatus(DownloadStatus())
		self.logger.info('downloading scene: {0}'.format(x.id))

		n = settings.DOWNLOAD_TIMEOUT
		while n > 0 and not self.pausedDownloadT:
			try:
				code = self.d.download(x.id, x.status)
				if code != 0: raise Exception
				self.p_queue.append(x)
				self.logger.info('scene {0} downloaded, added to processing queue'.format(x.id))
				x.status = 'PENDING'
				break
			except:
				self.logger.info('scene {0} download failure, attempts remaining: ({1}/{2})'.format(x.id, n, settings.DOWNLOAD_TIMEOUT))
				x.status.reset()
				shutil.rmtree(generateFilePathStr(x.id, 'raw'))
				n -= 1
				time.sleep(2)

		if n == 0:
			self.logger.info('scene {0} download failure timeout, aborting'.format(x.id))


	def downloadHandler(self):
		while not self.shutdownT:
			if len(self.d_queue_man) > 0 and not self.pausedT and not self.pausedDownloadT:
				x = self.d_queue_man[0]
				self.downloadHelper(x)
				del self.d_queue_man[0]

			elif len(self.d_queue_auto) > 0 and not self.pausedT and not self.pausedDownloadT and len(self.p_queue) < 10:
				x = self.d_queue_auto[0]
				self.downloadHelper(x)
				del self.d_queue_auto[0]

			time.sleep(5)

		self.logger.info('shutdown detected and acknowledged by downloader')
		self.shutdownDownloadT = True
		return(0)


	def preprocHandler(self):
		while (not self.shutdownT) or (not self.shutdownDownloadT):
			if len(self.p_queue) > 0 and not self.pausedT and not self.pausedPreprocT:
				x = self.p_queue[0]
				self.logger.info('processing scene: {0}'.format(x.id))

				if check_scene_exists(x.id, self.db, self.cur):
					del self.p_queue[0]
					self.logger.info('scene {0} already in index, continuing'.format(x.id))
					continue

				x.updateStatus(PreProcStatus())
				message = self.p.preproc(x.id, x.status)
				if message == 0: self.logger.info('scene {0} processed'.format(x.id))
				else: self.logger.info('scene {0} processing failed'.format(x.id))
				del self.p_queue[0]
			time.sleep(5)

		self.logger.info('shutdown detected and acknowledged by preprocessor')
		self.shutdownPreprocT = True
		return(0)


	def shutdownHandler(self):
		while not self.shutdownT:
			time.sleep(5)
		self.logger.info('shutting down scheduler...')
		self.logger.info('waiting for threads to complete tasks before beginning cleanup...')
		self.shutdown()


	def shutdown(self):
		start = time.time()
		while not self.shutdownPreprocT or not self.shutdownDownloadT:
			if time.time() - start > 600:
				self.logger.warning('threads have failed to close, manually closing critical resources')
				self.logger.warning('wait for completion before termination - database may need cleanup after shutdown')
				break
			time.sleep(10)

		# shutdown preproc
		cleanup(self.p.db, self.p.cur, self.p.h5F)
		self.p.h5F.close()
		self.p.cur.close()
		self.p.db.close()
		self.logger.warning('HDF5 resources closed')

		# shutdown self
		self.cur.close()
		self.db.close()
		self.logger.warning('SQL resources closed')

		self.logger.warning('all resources have closed successfully')
		return(0)
