import os
import requests

from baseimage.config import CONFIG
from baseimage.path_resolution import generate_file_path, check_create_folder
from service_collect_landsat.src.data_import_utils import (
	url_builder,
	remote_file_exists,
	scene_interpreter
)


class Downloader(object):
	def __init__(self, logger):
		self.logger = logger
		self.google_api_url = CONFIG['google_api_url']


	def download(self, sceneid):
		check_create_folder(generate_file_path(CONFIG['data_dir'], sceneid, 'raw'))

		interpScene = scene_interpreter(sceneid)
		url = self.get_url(interpScene)
		check = remote_file_exists(url)

		if remote_file_exists(url):
			r = requests.get(url, stream=True, timeout=5)
			f = open(generate_file_path(CONFIG['data_dir'], sceneid, 'raw', 'tar'), 'wb')
			for chunk in r.iter_content(chunk_size=2048):
				if chunk:
					f.write(chunk)
			f.close()

		else:
			raise Exception("scene {} was not found on the remote server")


	def get_url(self, sat):
		""" gets google download url given an interpreted scene ID
		"""
		filename = sat['scene'] + '.tar.bz'
		return url_builder([self.google_api_url, sat['sat'], sat['path'], sat['row'], filename])
