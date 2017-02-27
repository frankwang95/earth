import random
import sys
from PIL import Image
Image.MAX_IMAGE_PIXELS = 1000000000
import numpy as np
from sklearn.cluster import KMeans

sys.path.insert(0,'..')
from utils import generateFilePathStr



@profile
def testKMeans(sceneid):
	image = np.array(Image.open(generateFilePathStr(sceneid, 'preproc', 'visible')), dtype = 'float64') / 255
	
	points = [(random.randint(1, image.shape[0] - 2), random.randint(1, image.shape[1] - 2)) for _ in range(5000000)]
	data = np.empty((5000000, 27), dtype = 'float64')
	for i in range(5000000):
		data[i, 0:3] = image[points[i][0] - 1, points[i][1] - 1]
		data[i, 3:6] = image[points[i][0] - 1, points[i][1]]
		data[i, 6:9] = image[points[i][0] - 1, points[i][1] + 1]
		data[i, 9:12] = image[points[i][0], points[i][1] - 1]
		data[i, 12:15] = image[points[i][0], points[i][1]]
		data[i, 15:18] = image[points[i][0], points[i][1] + 1]
		data[i, 18:21] = image[points[i][0] + 1, points[i][1] - 1]
		data[i, 21:24] = image[points[i][0] + 1, points[i][1]]
		data[i, 24:27] = image[points[i][0] + 1, points[i][1] + 1]

	kmeans = KMeans(n_clusters = 3).fit(data)

	for i in range(5000000):
		if kmeans.labels_[i] == 0:
			image[points[i][0], points[i][1], 0] = 1
			image[points[i][0], points[i][1], 1] = 0
			image[points[i][0], points[i][1], 2] = 0
		if kmeans.labels_[i] == 1:
			image[points[i][0], points[i][1], 0] = 0
			image[points[i][0], points[i][1], 1] = 1
			image[points[i][0], points[i][1], 2] = 0
		if kmeans.labels_[i] == 2:
			image[points[i][0], points[i][1], 0] = 0
			image[points[i][0], points[i][1], 1] = 0
			image[points[i][0], points[i][1], 2] = 1

	image *= 255
	image = image.astype('uint8')
	Image.fromarray(image).show()



testKMeans('LC80210422016146LGN00')