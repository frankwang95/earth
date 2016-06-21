from os.path import join, exists, getsize
import os
import sys
import requests

sys.path.insert(0,'..')
from dataImportUtils import(
	url_builder,
	remote_file_exists,
	get_remote_file_size,
	scene_interpreter,
	DownloadStatus
)
from utils import generateFilePathStr, ExceptionObj, check_create_folder,
import dataImportSettings as settings



class Downloader(object):
	def __init__(self):
		self.status = 'IDLE'
		self.google = settings.GOOGLE_STORAGE
		self.s3 = settings.S3_LANDSAT
		check_create_folder(generateFilePathStr())


	def download(self, sceneid, status=None):
		if os.path.exists(generateFilePathStr(sceneid)):
			return(ExceptionObj('scene {0} already exists'.format(sceneid)))
		check_create_folder(generateFilePathStr(sceneid))

		return(self.google_storage(sceneid, status))
		#if code != 0: self.amazon_s3(scene)


	def google_storage(self, sceneid, status):
		interpScene = scene_interpreter(sceneid)
		url = self.google_storage_url(interpScene)
		check = remote_file_exists(url)

		if check == 0: return(self.fetch(url, sceneid, status))
		return(check)


	def amazon_s3(self, scene, bands):
		interpScene = scene_interpreter(scene)
		url = None
		check = remote_file_exists(url)
		return(check)


	### gets google download url given an interpreted scene ID
	def google_storage_url(self, sat):
		filename = sat['scene'] + '.tar.bz'
		return url_builder([self.google, sat['sat'], sat['path'], sat['row'], filename])


	### gets amazon url given an interpreted scene ID
	def amazon_s3_url(self, sat):
		if band != 'MTL':
			filename = '%s_B%s.TIF' % (sat['scene'], band)
		else:
			filename = '%s_%s.txt' % (sat['scene'], band)
		return url_builder([self.s3, sat['sat'], sat['path'], sat['row'], sat['scene'], filename])


	def fetch(self, url, sceneid, status):
		if status==None:
			self.status = DownloadStatus()
		else: self.status = status

		self.status.updateTotal(get_remote_file_size(url))

		r = requests.get(url, stream = True)
		f = open(generateFilePathStr(sceneid, file = 'tar'), 'wb')
		for chunk in r.iter_content(chunk_size=2048): 
			if chunk:
				f.write(chunk)
				self.status.updateProg(len(chunk))
		f.close()

		self.status.completed()
		self.status = 'IDLE'
		return(0)
