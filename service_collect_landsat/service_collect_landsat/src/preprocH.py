import h5py
import numpy as np
import scipy.ndimage
import functools as fT
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000

from baseimage.path_resolution import generate_file_path, check_create_folder
from service_collect_landsat.src.cython import (
	pyBilinearInter,
	pyLuminosityBlend,
	pyAdjustLevels,
	py16to8,
	pyDownsize
)


############################### IMAGERY #############################
bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B8', 'B9', 'B10', 'B11', 'BQA']


############################### PROCESS #############################
class LandsatPreProcess:
	""" Class which implements the each of the functions applied to an landsat image at the time of insertion into our
		databases. The class is instantiated for a fixed landsat image which must have already been downloaded. For detailed
		documentation of the structure of data store see the files in data-collection/documentation/.

	Args:
		data_dir <str>: The path to the root data directory. Needed to derive the filepath to the uncompressed downloaded
			file and the paths where the completed images are placed.
		sceneid <str>: The landsat ID of the scene to be processed.
	"""
	def __init__(self, data_dir, sceneid):
		self.data_dir = data_dir
		self.id = sceneid
		self.visible = None

		self.images = {}
		# for b in bands:
		# 	self.images[b] = np.array(Image.open(generate_file_path(self.data_dir, sceneid, 'raw', b)), dtype = 'uint16')


	def generateVisible(self):
		""" Computes a RGB 8-bit color image array from the separated 1-channel 16-bit R, G, and B channels included in the
			raw data and makes it avaialbe under the `visible` attribute of this class.
		"""
		self.visible = np.dstack((
			self.images['B4'],
			self.images['B3'],
			self.images['B2']
		))
		pyAdjustLevels(self.visible)


	def generateDownsize(self):
		""" Computes downsized versions of each raw band and replaces the original full size arrays stored in the `image`
			attribute of each class. Each new array is half (rounded down) the width and length of the orignal arrays.
		"""
		for b in bands:
			outRes = np.zeros((int(self.images[b].shape[0]/2), int(self.images[b].shape[1]/2)), dtype='uint16')
			pyDownsize(self.images[b], outRes)
			self.images[b] = outRes

			outBit = outRes = np.zeros((self.images[b].shape[0], self.images[b].shape[1]), dtype='uint8')
			py16to8(self.images[b], outBit)
			self.images[b] = outBit


	def generatePanVisible(self):
		""" Implements the logic for generating an upsampled visible image using the larger B8 band. The resulting upsampled
			image is stored under the `visibleInter` attribute of this class.

			Note: This method is not currently a part of the defined process pipeline and is being included here for reference.
		"""
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


	def writeHDF(self):
		""" Writes the computed downsized raw arrays into the HDF5 file store.
		"""
		with h5py.File(generate_file_path(self.data_dir, kind='database'), 'a', libver='latest') as h5F:
			h5F.create_group(self.id)
			for b in bands:
				h5F.create_dataset(generate_file_path(self.data_dir, self.id, 'database', b), data=self.images[b], chunks=True)


	def writeVis(self):
		""" Writes the computed visible image to a jpeg in the preprocessed folder. Must be called after generateVisible.
		"""
		Image.fromarray(self.visible).save(generate_file_path(self.data_dir, self.id, 'preproc', 'visible'))


	def metadataInsert(self, db, cur):
		""" Writes the metadata found with the landsat scene to our MySQL database.
		"""
		with open(generate_file_path(self.data_dir, self.id, 'raw', 'metadata'), 'r') as h:
			rawMetaData = h.readlines()

		splitTags = [i.strip().split(' = ') for i in rawMetaData]
		splitTags = {x[0]:x[1] for x in splitTags if len(x) >= 2}

		row = splitTags['WRS_ROW']
		col = splitTags['WRS_PATH']
		time = splitTags['DATE_ACQUIRED'] + ' ' + splitTags['SCENE_CENTER_TIME'][1:9]
		ul_lat = splitTags['CORNER_UL_LAT_PRODUCT']
		ul_lon = splitTags['CORNER_UL_LON_PRODUCT']
		ur_lat = splitTags['CORNER_UR_LAT_PRODUCT']
		ur_lon = splitTags['CORNER_UR_LON_PRODUCT']
		ll_lat = splitTags['CORNER_LL_LAT_PRODUCT']
		ll_lon = splitTags['CORNER_LL_LON_PRODUCT']
		lr_lat = splitTags['CORNER_LR_LAT_PRODUCT']
		lr_lon = splitTags['CORNER_LR_LON_PRODUCT']
		ul_proj_x = splitTags['CORNER_UL_PROJECTION_X_PRODUCT']
		ul_proj_y = splitTags['CORNER_UL_PROJECTION_Y_PRODUCT']
		ur_proj_x = splitTags['CORNER_UR_PROJECTION_X_PRODUCT']
		ur_proj_y = splitTags['CORNER_UR_PROJECTION_Y_PRODUCT']
		ll_proj_x = splitTags['CORNER_LL_PROJECTION_X_PRODUCT']
		ll_proj_y = splitTags['CORNER_LL_PROJECTION_Y_PRODUCT']
		lr_proj_x = splitTags['CORNER_LR_PROJECTION_X_PRODUCT']
		lr_proj_y = splitTags['CORNER_LR_PROJECTION_Y_PRODUCT']
		cloud_cover = splitTags['CLOUD_COVER']
		roll_angle = splitTags['ROLL_ANGLE']
		sun_azimuth = splitTags['SUN_AZIMUTH']
		sun_elev = splitTags['SUN_ELEVATION']
		earth_sun_dist = splitTags['EARTH_SUN_DISTANCE']
		orientation = splitTags['ORIENTATION']

		enterCmd = u'''INSERT INTO imageindex VALUES ('{0}', '{1}', {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23}, {24}, {25});'''.format(
		    self.id,
		    time,
		    ul_lat, ul_lon, ur_lat, ur_lon, ll_lat, ll_lon, lr_lat, lr_lon,
		    ul_proj_x, ul_proj_y, ur_proj_x, ur_proj_y, ll_proj_x, ll_proj_y, lr_proj_x, lr_proj_y,
		    cloud_cover,
		    roll_angle,
		    sun_azimuth,
		    sun_elev,
		    earth_sun_dist,
		    orientation,
			row,
			col
		)

		cur.execute(enterCmd)
		db.commit()
