import time
import MySQLdb as sql

from lib_learning.collection.base_generator import WorkBlockGenerator
from collection_landsat.src.data_import_utils import check_scene_exists


class LandSatLocalIndexBlockGenerator(WorkBlockGenerator):
    def __init__(self, sql_parameters):
        self.sql_parameters = sql_parameters
        self.worked_items = {}


    def check_scene_exists(self, sceneid):
        db = sql.connect(**self.sql_parameters)
        cur = db.cursor()
        return check_scene_exists(sceneid, db, cur)


    def get_random_lid(self):
        query = "SELECT lid FROM remote_imageindex ORDER BY RAND() LIMIT 1"
        db = sql.connect(**self.sql_parameters)
        cur = db.cursor()
        cur.execute(query)
        return cursor.fetchall()[0][0]


    def get_next(self, lid=None):
        if lid is None:
            lid = self.get_random_lid()

        if self.check_scene_exists(lid) or lid in self.worked_items:
            return {}

        self.worked_items[lid] = time.time()
        return {'lid': lid}
