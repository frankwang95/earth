import MySQLdb as sql
import threading
from queue import Queue

from baseimage.logger import get_default_logger
from baseimage.config import CONFIG
from baseimage.path_resolution import generate_file_path, check_create_folder
import service_collect_landsat.src.download as download
import service_collect_landsat.src.preproc as preproc
from service_collect_landsat.src.data_import_utils import check_scene_exists


class Scheduler:
	def __init__(self):
		# check data directory installation
		check_create_folder(generate_file_path(CONFIG['data_dir']))
		check_create_folder(generate_file_path(CONFIG['data_dir'], kind='raw'))
		check_create_folder(generate_file_path(CONFIG['data_dir'], kind='preproc'))
		check_create_folder(generate_file_path(CONFIG['data_dir'], kind='preproc', file='visible'))

		# core resources
		self.logger = get_default_logger()
		self.d = download.Downloader(self.logger)
		self.p = preproc.Preprocessor(self.logger)
		self.d_queue = Queue()
		self.p_queue = Queue()
		self.item_hash = {}
		self.push_lock = threading.Lock()
		self.sql_parameters = {
			'db': CONFIG['mysql']['db'],
			'host': CONFIG['mysql']['host'],
			'user': CONFIG['mysql']['user'],
			'passwd': CONFIG['mysql']['pass']
		}

		# start modules
		self.logger.info('scheduler started')
		d_thread = threading.Thread(target=self.download_handler)
		p_thread = threading.Thread(target=self.preprocess_handler)
		d_thread.setDaemon(True)
		p_thread.setDaemon(True)
		d_thread.start()
		p_thread.start()


	def push(self, sceneid):
		with self.push_lock:
			if not self.check_scene_exists(sceneid) and sceneid not in self.item_hash:
				self.d_queue.put(sceneid)
				self.item_hash[sceneid] = True
				self.logger.info('scene {0} inserted into download queue'.format(sceneid))
				return

			self.logger.warning('scene {0} already in image index'.format(sceneid))



	def download_handler(self):
		while True:
			x = self.d_queue.get()
			self.logger.info('downloading scene: {0}'.format(x))
			try:
				self.d.download(x)
				self.logger.info('scene {0} downloaded, added to processing queue'.format(x))
				self.p_queue.put(x)
			except:
				self.logger.exception('failed to download scene {0}'.format(x))


	def preprocess_handler(self):
		while True:
			x = self.p_queue.get()
			self.logger.info('processing scene: {0}'.format(x))

			try:
				self.p.preproc(x)
				del self.item_hash[x]
				self.logger.info('scene {0} processed'.format(x))
			except:
				self.logger.exception('failed to process scene {0}'.format(x))


	def get_d_queue(self):
		return list(self.d_queue.queue)


	def get_p_queue(self):
		return list(self.p_queue.queue)


	def check_scene_exists(self, sceneid):
		db = sql.connect(**self.sql_parameters)
		cur = db.cursor()
		return check_scene_exists(sceneid, db, cur)
