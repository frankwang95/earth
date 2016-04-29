import os
import numpy as np
import tifffile as tif

import settings
from util import(
	ExceptionObj
)



##### 16-Bit Greyscale or RGB Tiff representations via Numpy
class LandsatTIFF:
	def __init__(self, src):
		if isinstance(src, str): self.array = tif.imread(src)
		if isinstance(src, np.ndarray): self.array = src
		self.raster_dim = self.array.shape


	def write(self, filename):
		tif.imsave(filename, self.array)
		return(0)


	def autoLevels(self):
		return(0)



class LandsatScene:
	def __init__(self, sceneid):
		self.id = sceneid
		self.metadata = None #Get from SQL
		self.filenames = os.listdir(settings.IN_DATA_DIR + '/' + str(sceneid)) #Get from SQL

		self.images = {}
		for j in self.filenames:
			band = j.replace('.', '_').split('_')[1]
			ext = j.replace('.', '_').split('_')[2]
			if ext == 'TIF':
				self.images[band] = LandsatTIFF(settings.IN_DATA_DIR + '/' + str(sceneid) + '/' + j)

		self.visible = False
		self.pansharpened = False


	def genVisible(self):
		self.visible = LandsatTIFF(np.dstack((
			self.images['B4'].array,
			self.images['B3'].array,
			self.images['B2'].array
		)))
		return(0)


	def panSharpen(self):
		return(0)



#img = ImageTif(settings.IN_DATA_DIR + '/LC81420402016114LGN00/marbles.tif')
#print img.write(settings.IN_DATA_DIR + '/LC81420402016114LGN00/marbles.jpg')

scn = LandsatScene('LC81420402016114LGN00')
scn.genVisible()
#np.savetxt('array.txt', scn.images['B2'].array)
scn.visible.write(settings.IN_DATA_DIR + '/LC81420402016114LGN00/' + 'test.TIF')