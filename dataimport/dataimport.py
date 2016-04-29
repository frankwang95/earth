import datetime
from calendar import monthrange
import search
import settings
import download



class DownloadScheduler:
	def __init__(self):
		self.t = datetime.datetime.now()
		self.s = search.Search()
		self.d = download.Downloader()

		print(self.getSearch(03, 2016))


	def getSearch(self, mon, yr):
		nDays = (datetime.date(yr, mon, 1) - datetime.date(yr, mon, 1)).days
		results = self.s.search(
			start_date = '{0}-{1}-01'.format(yr, mon),
			end_date = '{0}-{1}-{2}'.format(yr, mon, nDays),
			cloud_max = settings.CLOUD_MAX
			limit = 10000
		)
		if results['status'] == u'SUCCESS': return(results['results'])
		return(1)


	def getDownload(self, key):
		return(0)

DownloadScheduler()