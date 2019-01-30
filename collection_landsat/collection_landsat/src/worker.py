import MySQLdb as sql
import threading
from queue import Queue

from lib_core.path_resolution.path_resolution import generate_file_path, check_create_folder
import collection_landsat.src.download as download
import collection_landsat.src.preproc as preproc
from collection_landsat.src.data_import_utils import check_scene_exists


class LandSatLocalIndexTask(object):
	def __init__(self, logger, data_dir, sql_parameters, base_api_url):
		self.logger = logger
		self.data_dir = data_dir
		self.base_api_url = base_api_url
		self.sql_parameters = sql_parameters

		# check data directory installation
		check_create_folder(generate_file_path(self.data_dir))
		check_create_folder(generate_file_path(self.data_dir, kind='raw'))
		check_create_folder(generate_file_path(self.data_dir, kind='preproc'))
		check_create_folder(generate_file_path(self.data_dir, kind='preproc', file='visible'))

		self.d = download.Downloader(self.data_dir, self.base_api_url, self.logger)
		self.p = preproc.Preprocessor(self.data_dir, self.sql_parameters, self.logger)


	def main(self, work_block):
		# Existing scenes are not reprocessed, the block generator returns an empty work block
		if 'lid' not in work_block:
			return

		sceneid = work_block['lid']
		if self.check_scene_exists(sceneid):
			self.logger.warning('lid {} already found in local image index'.format(sceneid))
			return
		self.d.download(sceneid)
		self.p.preproc(sceneid)


	def check_scene_exists(self, sceneid):
		db = sql.connect(**self.sql_parameters)
		cur = db.cursor()
		return check_scene_exists(sceneid, db, cur)
