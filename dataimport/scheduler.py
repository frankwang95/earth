import threading
import random
import datetime
import time
from calendar import monthrange

import settings
import search
import download
import extraction
from utils import(
	DownloadStatus,
	ExtractionStatus
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



class DownloadScheduler:
	def __init__(self):
		self.s = search.Search()
		self.d = download.Downloader()
		self.e = extraction.Extractor()

		self.d_queue_auto = []
		self.d_queue_man = []
		self.e_queue = []

		threading.Thread(target = self.monthlyAutoSched).start()
		time.sleep(10)
		self.test = self.d_queue_auto[0]
		threading.Thread(target = self.testPrint).start()
		threading.Thread(target = self.downloadHandler).start()
		threading.Thread(target = self.extractionHandler).start()


	def testPrint(self):
		while True:
			try:
				print ('{0}/{1}'.format(self.test.status.prog, self.test.status.tot))
				print ('Done: {0}'.format(self.test.status.complete))
				print ('\n')
			except: print(self.test.status)
			time.sleep(5)


	def getSearch(self, mon, yr):
		nDays = monthrange(yr, mon)[1]
		results = self.s.search(
			start_date = '{0}-{1}-01'.format(yr, mon),
			end_date = '{0}-{1}-{2}'.format(yr, mon, nDays),
			cloud_max = settings.CLOUD_MAX,
			limit = 10000
		)
		if results['status'] == u'SUCCESS': return(results['results'])
		return(1)


	def monthlyAutoSched(self):
		month = None
		year = None
		while True:
			searchTime = datetime.datetime.now() - datetime.timedelta(days=settings.DAY_DELAY)
			if searchTime.month != month:
				self.d_queue_auto = []
				month = searchTime.month
				year = searchTime.year
				searchResults = [str(i['sceneID']) for i in self.getSearch(month, year)]
				random.shuffle(searchResults)
				self.d_queue_auto = [Task(i) for i in searchResults]
			time.sleep(43200)


	def downloadHandler(self):
		while True:
			if len(self.d_queue_man) > 0:
				x = self.d_queue_man.pop(0)
				x.updateStatus(DownloadStatus())
				self.d.download(x.id, x.status)
				self.e_queue.append(x)
				continue

			elif len(self.d_queue_auto) > 0:
				x = self.d_queue_auto.pop(0)
				x.updateStatus(DownloadStatus())
				self.d.download(x.id, x.status)
				self.e_queue.append(x)
				continue

			time.sleep(5)
		return(0)


	def extractionHandler(self):
		while True:
			if len(self.e_queue) > 0:
				x = self.e_queue.pop(0)
				x.updateStatus(ExtractionStatus())
				self.e.extract(x.id, x.status)
		return(0)


d = DownloadScheduler()