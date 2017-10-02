import os
import gc
import h5py
import tarfile
import numpy as np
import scipy.ndimage
import functools as fT
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000

from earth.utils import (
	ExceptionObj,
	generateFilePathStr,
	check_create_folder
)

from earth.data_import.cython import (
	pyBilinearInter,
	pyLuminosityBlend,
	pyAdjustLevels,
	py16to8,
	pyDownsize
)



############################### TAR COMPRESSION/DECOMPRESSION #############################
def decomTar(path, target, status):
    tar = tarfile.open(path)
    members = tar.getmembers()
    for m in members:
        tar.extract(m, target)
        status.updateProg()
    tar.close()



############################### IMAGERY #############################
bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'BQA']



############################### PROCESS #############################
class LandsatPreProcess:
	def __init__(self, sceneid, h5F):
		self.id = sceneid
		
		self.images = {}
		for b in bands:
			self.images[b] = np.array(Image.open(generateFilePathStr(sceneid, 'raw', b)), dtype = 'uint16')
		self.visible = False
		self.h5F = h5F


	def generateVisible(self):
		if type(self.visible) == type(True):
			self.visible = np.dstack((
				self.images['B4'],
				self.images['B3'],
				self.images['B2']
			))	
			pyAdjustLevels(self.visible)
		return(0)


	def generateDownsize(self):
		for b in bands:
			outRes = np.zeros((self.images[b].shape[0]/2, self.images[b].shape[1]/2), dtype='uint16')
			pyDownsize(self.images[b], outRes)
			self.images[b] = outRes

			outBit = outRes = np.zeros((self.images[b].shape[0], self.images[b].shape[1]), dtype='uint8')
			py16to8(self.images[b], outBit)
			self.images[b] = outBit


	def compute(self):
		self.generateDownsize()
		self.generateVisible()


	def writeHDF_MAIN(self):
		self.h5F.create_group(self.id)
		for b in bands:
			self.h5F.create_dataset(generateFilePathStr(self.id, 'database', b), data=self.images[b], chunks=True)
		return(0)


	def writeVis_MAIN(self):
		Image.fromarray(self.visible).save(generateFilePathStr(self.id, 'preproc', 'visible'))
		return(0)


	def close(self):
		del self.images
		del self.visible
		return(0)


	# CURRENTLY OUT OF PRODUCTION
	def writePanVis_MAIN(self): # code 1
		self.generatePanVisible()
		writeImg(self.visibleInter, generateFilePathStr(self.id, 'preproc', 'visible'))
		return(0)


	# CURRENTLY OUT OF PRODUCTION
	def generatePanVisible(self):
		if type(self.visibleInter) == type(True):
			self.generateVisible()

			self.visibleInter = np.ones((
				2 * self.visibleOrig.shape[0] - 1,
				2 * self.visibleOrig.shape[1] - 1,
				3), dtype = 'uint16'
			)
			pyBilinearInter(self.visibleOrig, self.visibleInter)

			# performs pansharpening
			pyLuminosityBlend(self.visibleInter, self.images['B8'])

			# adjusts levels
			pyAdjustLevels(self.visibleInter)
		return(0)
