import os
import time
from os.path import exists, getsize
import MySQLdb as sql
import tarfile

from baseimage.config import CONFIG
from collection_landsat.src.data_import_utils import purge_scene
from baseimage.path_resolution import generate_file_path
from collection_landsat.src.preprocH import *



############################# PREPROCESSOR CLASS #############################
class Preprocessor(object):
    def __init__(self, logger):
        self.logger = logger
        self.data_dir = CONFIG['data_dir']
        self.sql_parameters = {
            'db': CONFIG['mysql']['db'],
            'host': CONFIG['mysql']['host'],
            'user': CONFIG['mysql']['user'],
            'passwd': CONFIG['mysql']['pass']
        }


    def preproc(self, sceneid):
        if not os.path.exists(generate_file_path(self.data_dir, sceneid, 'raw')):
            self.logger.exception('scene {} not yet downloaded'.format(sceneid))
            return

        db = sql.connect(**self.sql_parameters)
        cur = db.cursor()

        try:
            with tarfile.open(generate_file_path(self.data_dir, sceneid, 'raw', 'tar')) as tar:
                tar.extractall(generate_file_path(self.data_dir, sceneid, 'raw'))
            os.remove(generate_file_path(self.data_dir, sceneid, 'raw', 'tar'))

            preProcObj = LandsatPreProcess(self.data_dir, sceneid)
            preProcObj.generateDownsize()
            preProcObj.generateVisible()
            preProcObj.writeHDF()
            preProcObj.writeVis()
            preProcObj.metadataInsert(db, cur)

        except:
            self.logger.exception('problem encountered while preprocessing scene: {}'.format(sceneid))
            self.logger.info('attempting to cleanup after preprocessing failure in scene {}'.format(sceneid))
            with h5py.File(generate_file_path(self.data_dir, kind='database'), 'a', libver='latest') as h5F:
                purge_scene(sceneid, self.data_dir, db, cur, h5F)

        cur.close()
        db.close()
        self.logger.info('scene {} successfully processed'.format(sceneid))
        return
