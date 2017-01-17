import os
import sys
import gc
import numpy as np
import scipy.ndimage
import functools as fT
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000
import tarfile
import h5py

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


def writeImg(imgArray, filepath):
	newarray = np.empty(imgArray.shape, dtype = 'uint8')
	py16to8(imgArray, newarray)
	Image.fromarray(newarray).save(filepath)
	return(0)



############################### PROCESS #############################
class LandsatPreProcess:
	def __init__(self, sceneid, h5F):
		self.id = sceneid
		
		self.images = {}
		for b in bands:
			self.images[b] = np.array(Image.open(generateFilePathStr(sceneid, 'raw', b)), dtype = 'uint16')
		self.visible = False
		self.h5File = h5F


	def generateVisible(self):
		if type(self.visible) == type(True):
			self.visible = np.dstack((
				self.images['B4'],
				self.images['B3'],
				self.images['B2']
			))	
			#pyAdjustLevels(self.visible)
		return(0)


	def generateDownsize(self):
		if self.images['B1'].shape[0] % 2 != 0:
			for b in bands:
				self.images[b] = self.images[b][:-1, :]
		if self.images['B1'].shape[1] % 2 != 0:
			for b in bands:
				self.images[b] = self.images[b][:, :-1]

		n = self.images['B1'].shape[0] / 2
		m = self.images['B1'].shape[1] / 2

		for b in bands:
			outRes = np.zeros((n, m), dtype='uint16')
			pyDownsize(self.images[b], outRes)
			self.images[b] = outRes

			outBit = outRes = np.zeros((n, m), dtype='uint8')
			py16to8(self.images[b], outBit)
			self.images[b] = outBit


	def compute(self):
		self.generateDownsize()
		self.generateVisible()


	def writeHDF_MAIN(self): # code 0
		self.h5File.create_group(self.id)
		for b in bands:
			self.h5File.create_dataset(generateFilePathStr(self.id, 'database', b), data=self.images[b], chunks=True)
		return(0)


	def writeVis_MAIN(self): # code 1
		writeImg(self.visible, generateFilePathStr(self.id, 'preproc', 'visible'))
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
