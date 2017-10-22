import MySQLdb as sql
from sqlalchemy import create_engine
import random
import h5py
import numpy as np
import pandas as pd
import time
from PIL import Image
import threading
import sklearn.cluster as cluster

from earth.data_import.dataImportUtils import generateFilePathStr
import earth.settings as settings


class DataLabelLoader(object):
    def __init__(self):
        print "Loader started"
        self.paused = False
        self.bands = ['B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7', 'B9', 'BQA']
        self.grid_size = 16
        self.dataset_size = 100000
        self.processed_outputs = {}

        thread = threading.Thread(target=self.main_loop)
        thread.daemon = True
        thread.start()


    def main_loop(self):
        while not self.paused:
            if len(self.processed_outputs) >= 8: time.sleep(10)

            lid = self.choose_lid()
            print "Processing {}...".format(lid)
            dataset, reference_df = self.get_dataset(lid, self.dataset_size)
            self.process_image(lid, dataset, reference_df)
            print "Done."


    def choose_lid(self):
        db = sql.connect(
            host=settings.DB_HOST, user=settings.DB_USER,
            passwd=settings.DB_PASS, db=settings.DB
        )
        cur = db.cursor()
        cur.execute('SELECT lid FROM imageindex order by RAND() LIMIT 1;')
        return cur.fetchall()[0][0]


    def get_dataset(self, sceneid, n):
        x_list = []
        y_list = []
        dataset = np.empty((n, len(self.bands) * self.grid_size ** 2))

        with h5py.File(generateFilePathStr(kind = 'database'), 'r') as h5F:
            for j in range(n):
                subimage = np.array(0)
                while (subimage == 0).any():
                    dim = h5F[sceneid][self.bands[0]].shape
                    subimage = np.empty((len(self.bands), self.grid_size, self.grid_size))
                    x = random.randint(self.grid_size / 2, dim[0] - self.grid_size / 2 - 1)
                    y = random.randint(self.grid_size / 2, dim[1] - self.grid_size / 2 - 1)

                    for i, b in enumerate(self.bands):
                        subimage[i] = h5F[sceneid][b][
                            x - self.grid_size / 2 : x + self.grid_size / 2,
                            y - self.grid_size / 2 : y + self.grid_size / 2
                        ]

                dataset[j] = subimage.flatten()
                x_list.append(x)
                y_list.append(y)

        reference_df = pd.DataFrame({'x_coord': x_list, 'y_coord': y_list})
        return dataset, reference_df


    def process_image(self, lid, dataset, reference_df):
        cluster_labels = cluster.KMeans(2).fit_predict(dataset)
        group1 = reference_df[cluster_labels==0][['x_coord', 'y_coord']].values
        group2 = reference_df[cluster_labels==1][['x_coord', 'y_coord']].values

        image = np.asarray(Image.open(generateFilePathStr(lid, 'preproc', 'visible'))).copy()
        for i in range(group1.shape[0]):
            x = group1[i,0]
            y = group1[i, 1]
            image[x-1:x+2, y-1:y+2, 0] = 255
        for i in range(group2.shape[0]):
            x = group2[i,0]
            y = group2[i, 1]
            image[x-1:x+2, y-1:y+2, 1] = 255
        image = Image.fromarray(image)
        image.save(generateFilePathStr(lid, 'preproc', 'cloud_detection_kmeans2'))
        image.thumbnail((1200, 1200))

        self.processed_outputs[lid] = {
            'cluster_labels': cluster_labels,
            'reference_df': reference_df,
            'image': image,
        }


    def write_results(self, lid, group):
        reference_df = self.processed_outputs[lid]['reference_df']
        cluster_labels = self.processed_outputs[lid]['cluster_labels']

        reference_df['lid'] = lid
        if group is not None:
            reference_df['label'] = 1
            reference_df['label'].loc[np.isin(cluster_labels, group)] = 0
        else: reference_df['label'] = 2

        conn = create_engine("mysql://{}@{}/{}".format(
            settings.DB_USER, settings.DB_HOST, settings.DB
        ))
        reference_df.to_sql('cloud_detection_kmeans2', conn, if_exists='append', index=False)
        del self.processed_outputs[lid]
