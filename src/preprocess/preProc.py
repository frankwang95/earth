import os
import sys
import gc

import numpy as np
import scipy.ndimage
import functools as fT
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000

sys.path.insert(0,'..')
sys.path.insert(0,'./cython')
from utils import (
	ExceptionObj,
	generateFilePathStr,
	check_create_folder
)
from pyPreProcPipe import (
	pyBilinearInter,
	pyLuminosityBlend,
	pyAdjustLevels,
	py16to8,
	pyWrite3x3
)
from georeference import *



bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'BQA']

def write(array, filepath):
	newarray = np.empty(array.shape, dtype = 'uint8')
	py16to8(array, newarray)
	Image.fromarray(newarray).save(filepath)
	return(0)


##### Object containing all image data for a raw landsat scene
class LandsatPreProcess:
	def __init__(self, sceneid):
		self.id = sceneid
		check_create_folder(generateFilePathStr(self.id, 'preproc'))
		filelist = os.listdir(generateFilePathStr())

		self.images = {}
		for b in bands:
			check_create_folder(generateFilePathStr(self.id, 'preproc', b))
			self.images[b] = np.array(Image.open(generateFilePathStr(sceneid, 'raw', b)), dtype = 'uint16')


	def generat3x3(self):
		pyWrite3x3(self.images['B1'], generateFilePathStr(self.id, 'preproc', 'B1'))
		return(0)


	def generate50x50(self):
		return(0)


	@profile
	def generateVisible(self):
		visibleOrig = np.dstack((
			self.images['B4'],
			self.images['B3'],
			self.images['B2']
		))
		visibleInter = np.ones((
			2 * visibleOrig.shape[0] - 1,
			2 * visibleOrig.shape[1] - 1,
			3), dtype = 'uint16'
		)
		pyBilinearInter(visibleOrig, visibleInter)
		del visibleOrig
		gc.collect()

		# performs pansharpening
		pyLuminosityBlend(visibleInter, self.images['B8'])

		# adjusts levels
		pyAdjustLevels(visibleInter)

		write(visibleInter, generateFilePathStr(self.id, 'preproc', 'visible'))
		del visibleInter
		gc.collect()
		return(0)


	def execute(self):
		#self.generateVisible()
		self.generat3x3()
		return(0)

		

scn = LandsatPreProcess('LC80030722016116LGN00')
scn.execute()
