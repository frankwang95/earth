import MySQLdb as sql
import random
import h5py
import numpy as np
import pandas as pd
from PIL import Image

import earth.settings as settings


class DataLabelLoader(object):
    def __init__(self):
        self.kmeans = cluster.KMeans(2)

        self.bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B9', 'BQA']
        self.grid_size = 16
        self.dataset_size = 500000

        self.available_lids = None
        self.processed_lids = []
        self.processed_outputs = {}


    def main_loop(self):
        self.refresh_lids()
        lid = random.sample(self.available_lids, 1)
        dataset, reference_df = self.get_dataset(lid, self.dataset_size)
        self.process_image(dataset, reference_df)


    def refresh_lids(self, query):
        db = sql.connect(
            host=settings.DB_HOST, user=settings.DB_USER,
            passwd=settings.DB_PASS, db=settings.DB
        )
        cur = db.cursor()
        cur.execute('SELECT lid FROM imageindex;')
        self.available_lids = [item[0] for item in cur.fetchall()]


    def get_dataset(self, sceneid, n):
        x_list = []
        y_list = []
        dataset = np.empty((
            len(scenes) * n,
            len(self.bands) * self.grid_size ** 2
        ))

        with h5py.File(generateFilePathStr(kind = 'database'), 'r') as h5F:
            for i in range(n):
                subimage = np.array(0)
                while (subimage == 0).any():
                    dim = h5F[sceneid][self.bands[0]].shape
                    subimage = np.empty((len(self.bands), self.grid_size, self.grid_size))
                    x = random.randint(self.grid_size / 2, dim[0] - self.grid_size / 2 - 1)
                    y = random.randint(self.grid_size / 2, dim[1] - self.grid_size / 2 - 1)

                    for i, b in enumerate(self.bands):
                        subimage[i] = h5F[sceneid][b][
                            x - grid_size / 2 : x + grid_size / 2,
                            y - grid_size / 2 : y + grid_size / 2
                        ]

                dataset[i] = subimage.flatten()
                x_list.append(x)
                y_list.append(y)

        reference_df = pd.DataFrame({'x': x_list, 'y': y_list})
        return dataset, reference_df


    def process_image(self, lid, dataset, reference_df):
        cluster_labels = kmean.fit_predict(dataset)
        self.processed_outputs[lid] = {
            'group1': reference_df[cluster_labels==0][['x', 'y']].values,
            'group2': reference_df[cluster_labels==1][['x', 'y']].values,
            'image': np.array(Image.open(generateFilePathStr(lid, 'preproc', 'visible')))
        }
