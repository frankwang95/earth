from datetime import datetime
import requests

from lib_learning.collection.batch_writer import BatchWriter


class LandSatRemoteIndexEntry(object):
    def __init__(self, entry_dict):
        self.json = entry_dict

        self.scene_id = self.json['scene_id']
        self.category = self.json['category']
        self.sensor = self.json['sensor']
        self.satellite = self.json['satellite']
        self.path = self.json['path']
        self.row = self.json['row']
        self.aquisition_date = datetime.strptime(str(self.json['acquisition_date']), '%Y%m%d')
        self.sun_azimuth = self.json['sun_azimuth']
        self.sun_elevation = self.json['sun_elevation']
        self.cloud_coverage = self.json['cloud_coverage']
        # add geometry parsing

        if self.category == 'pre':
            self.ingestion_date = None
            self.correction_level = None

        else:
            self.ingestion_date = datetime.strptime(str(self.json['ingestion_date']), '%Y%m%d')
            self.correction_level = self.json['correction_level']


class LandSatRemoteIndexBatchWriter(BatchWriter):
    def __init__(self, logger, sql_parameters, batch_size=64):
        template = {
        	'scene_id': 'lid',
        	'aquisition_date': 'aquisition_date',
        	'ingestion_date': 'ingestion_date',
        	'category': 'category',
        	'correction_level': 'correction_level',
        	'ls_row': 'row',
        	'ls_path': 'path',
        	'cloud_coverage': 'cloud_cover',
        	'sun_azimuth': 'sun_azimuth',
        	'sun_elevation': 'sun_elev'
        }
        table_name = 'imageindex_remote'
        super().__init__(logger, template, table_name, sql_parameters, batch_size)


class LandSatRemoteIndexTask(object):
    def __init__(self, logger, sql_params):
        self.sql_params = sql_params
        self.batch_writer = LandSatRemoteIndexBatchWriter(logger, sql_params)


    def main(self, block):
        assert 'url' in block

        response = requests.get(block['url']).json()
        n_items = response['meta']['found']
        objects = [LandSatRemoteIndexEntry(item) for item in response['results']]

        for o in objects:
            self.batch_writer.push(o)
        self.batch_writer.flush()
