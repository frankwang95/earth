import time
import random
import sys

import MySQLdb as sql
import numpy as np
import h5py

sys.path.insert(0,'..')
from utils import generateFilePathStr
import settings



bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B9', 'B10', 'B11', 'BQA']


def generate_random_dataset(database_name, n, db, cur, h5F):
	data = np.empty(shape=(n, len(bands), 33, 33))

	sql_cmd = 'SELECT lid FROM imageindex;'
	cur.execute(sql_cmd)
	scene_list = [lid[0] for lid in cur.fetchall()]

	start = time.time()
	for i in range(n):

		s = random.choice(scene_list)
		dim = h5F[s][bands[0]].shape

		y = random.choice(range(16, dim[0]-17))
		x = random.choice(range(16, dim[1]-17))
		data[i,0,:,:] = h5F[s][bands[0]][y-16:y+17,x-16:x+17]
		while np.any(data[i,0,:,:] == 0):
			y = random.choice(range(16, dim[0]-17))
			x = random.choice(range(16, dim[1]-17))
			data[i,0,:,:] = h5F[s][bands[0]][y-16:y+17,x-16:x+17]

		for b in range(1, len(bands)):
			data[i,b,:,:] = h5F[s][bands[b]][y-16:y+17,x-16:x+17]

	print (time.time() - start)
	return(data)


##### MAIN ######
h5F = h5py.File(generateFilePathStr(type = 'database'), 'r')
db = sql.connect(
		db=settings.DB,
		host=settings.DB_HOST,
		user=settings.DB_USER,
		passwd=settings.DB_PASS
)
cur = db.cursor()

try:
	data = generate_random_dataset("random", 2000, db, cur, h5F)
	print data.shape
except Exception as e: print e

h5F.close()
cur.close()
db.close()
