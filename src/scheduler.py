##### TODO
# TESTING
	# NETWORK INTERUPTION HANDLING
# DISPLAY STATUS

import threading
import random
import datetime
import time
import sys
import os
from calendar import monthrange
import MySQLdb as sql

sys.path.insert(0,'./data_import')
import search
import download
import extraction
from dataImportUtils import(
	DownloadStatus,
	ExtractionStatus
)
from dataImportSettings import(
	CLOUD_MAX,
	DAY_DELAY
)
import settings
import schedulerIO



def checkScene(sceneid, db, cur):
	cur.execute("SELECT EXISTS (SELECT 1/0 FROM imageindex WHERE lid='{0}');".format(sceneid))
	return(cur.fetchall()[0][0] == 1)



class Task:
	def __init__(self, id):
		self.id = id
		self.status = 'PENDING'
		self.history = []


	def updateStatus(self, obj):
		self.history.append(self.status)
		self.status = obj
		return(0)



class DownloadScheduler:
	def __init__(self):
		self.shutdownT = False
		self.pausedT = False
		self.pausedDownloadT = False
		self.pausedExtractT = False

		self.log = []

		self.addLog('initializing scheduler...')
		self.db = sql.connect(
			db="earthdat",
			host=settings.DB_HOST,
			user=settings.DB_USER,
			passwd=settings.DB_PASS
		)
		self.cur = self.db.cursor()

		self.s = search.Search()
		self.d = download.Downloader()
		self.e = extraction.Extractor()

		self.d_queue_auto = []
		self.d_queue_man = []
		self.e_queue = []

		

		threading.Thread(target = self.monthlyAutoSched).start()
		threading.Thread(target = self.downloadHandler).start()
		threading.Thread(target = self.extractionHandler).start()

		self.addLog('initializing scheduler IO...')
		self.addLog('scheduler initialized')
		schedulerIO.SchedulerIO(self)

	# may need multiple searches to get all results
	def getSearch(self, mon, yr):
		nDays = monthrange(yr, mon)[1]
		results = self.s.search(
			start_date = '{0}-{1}-01'.format(yr, mon),
			end_date = '{0}-{1}-{2}'.format(yr, mon, nDays),
			cloud_max = CLOUD_MAX,
			limit = 4000
		)
		if results['status'] == u'SUCCESS': return(results['results'])
		time.sleep(30)

		return(1)


	def monthlyAutoSched(self):
		month = None
		year = None
		while not self.shutdownT:
			searchTime = datetime.datetime.now() - datetime.timedelta(days=DAY_DELAY)
			if searchTime.month != month and not self.pausedT:
				self.addLog('updating queue for new month ...')
				self.d_queue_auto = []
				month = searchTime.month
				year = searchTime.year
				searchResults = [str(i['sceneID']) for i in self.getSearch(month, year)]
				random.shuffle(searchResults)
				self.d_queue_auto = [Task(i) for i in searchResults if not checkScene(i, self.db, self.cur)]
				self.addLog('queue updated with {0} entries'.format(len(searchResults)))
			time.sleep(30)
		return(0)


	def downloadHandler(self):
		while not self.shutdownT:
			if len(self.d_queue_man) > 0 and not self.pausedT and not self.pausedDownloadT:
				x = self.d_queue_man[0]
				x.updateStatus(DownloadStatus())
				self.addLog('downloading scene: {0}'.format(x.id))
				self.d.download(x.id, x.status)
				self.e_queue.append(x)
				self.addLog('scene {0} downloaded, added to extraction queue'.format(x.id))
				x.status = 'PENDING'
				del self.d_queue_man[0]
				continue

			elif len(self.d_queue_auto) > 0 and not self.pausedT:
				x = self.d_queue_auto[0]
				x.updateStatus(DownloadStatus())
				self.addLog('downloading scene: {0}'.format(x.id))
				self.d.download(x.id, x.status)
				self.e_queue.append(x)
				self.addLog('scene {0} downloaded, added to extraction queue'.format(x.id))
				x.status = 'PENDING'
				del self.d_queue_auto[0]
				continue

			time.sleep(5)
		return(0)


	def extractionHandler(self):
		while not self.shutdownT:
			if len(self.e_queue) > 0 and not self.pausedT and not self.pausedExtractT:
				x = self.e_queue[0]
				self.addLog('extracting scene: {0}'.format(x.id))
				x.updateStatus(ExtractionStatus())
				self.e.extract(x.id, x.status)
				self.addLog('scene {0} extracted'.format(x.id))
				del self.e_queue[0]

		# Deletes unextracted downloads
		for task in self.e_queue:
			os.remove(generateFilePathStr(task.id, file = 'tar'))
			os.remove(generateFilePathStr(task.id))
		return(0)


	def addLog(self, str):
		self.log.append(time.strftime("[%H:%M:%S] ", time.localtime()) + 'SCHEDULER: ' + str)
		return(0)


	def shutdown(self):
		self.addLog('shutting down scheduler...')
		self.shutdownT = True
		self.addLog('waiting for threads to complete tasks (this can take a while)...')
		return(0)


d = DownloadScheduler()