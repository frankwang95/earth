import shutil
import re
import requests
import MySQLdb as sql
import random
import time
import sys

sys.path.insert(0,'..')
from datetime import datetime
from utils import generateFilePathStr



############################### STATUS OBJECT #############################
class DownloadStatus:
    def __init__(self, total=1):
        self.prog = 0
        self.tot = total
        self.complete = False

    def updateProg(self, change):
        self.prog += change
        return(0)

    def updateTotal(self, total):
        self.tot = total
        return(0)

    def reset(self):
        self.prog = 0
        return(0)

    def completed(self):
        self.complete = True
        return(0)



class PreProcStatus:
    def __init__(self):
        self.prog = 0
        self.tot = 15

    def updateProg(self, change=1):
        self.prog += change
        return(0)



############################### SQL #############################
def check_scene_exists(sceneid, db, cur):
    enterCmd = 'SELECT lid FROM imageindex WHERE lid="{0};"'.format(sceneid)
    code = cur.execute(enterCmd)
    return(code != 0)


def remove_scene(sceneid, db, cur):
    enterCmd = 'DELETE FROM imageindex WHERE lid="{0};"'.format(sceneid)
    cur.execute(enterCmd)
    return(0)


def metadataInsert(sceneid, db, cur):
    h = open(generateFilePathStr(sceneid, 'raw', 'metadata'), 'r')
    rawMetaData = h.readlines()
    h.close()

    splitTags = [i.strip().split(' = ') for i in rawMetaData]
    splitTags = {x[0]:x[1] for x in splitTags if len(x) >= 2}

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

    enterCmd = u'''INSERT INTO imageindex VALUES ('{0}', '{1}', {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13}, {14}, {15}, {16}, {17}, {18}, {19}, {20}, {21}, {22}, {23});'''.format(
        sceneid,
        time,
        ul_lat, ul_lon, ur_lat, ur_lon, ll_lat, ll_lon, lr_lat, lr_lon,
        ul_proj_x, ul_proj_y, ur_proj_x, ur_proj_y, ll_proj_x, ll_proj_y, lr_proj_x, lr_proj_y,
        cloud_cover,
        roll_angle,
        sun_azimuth,
        sun_elev,
        earth_sun_dist,
        orientation
    )

    cur.execute(enterCmd)
    db.commit()
    return(0)



############################### MISC #############################
def remove_slash(value):
    assert(isinstance(value, str))
    return re.sub('(^\/|\/$)', '', value)


def url_builder(segments):
    assert((isinstance(segments, list) or isinstance(segments, tuple)))
    return "/".join([remove_slash(s) for s in segments])


def threeDigitPad(number):
    number = str(number)
    if len(number) == 1:
        return u'00%s' % number
    elif len(number) == 2:
        return u'0%s' % number
    else:
        return(number)


def remote_file_exists(url):
    status = requests.head(url).status_code
    if status != 200:
        return(ExceptionObj('file at {0} does not exist on remote server'.format(url)))
    return(0)


def get_remote_file_size(url):
    headers = requests.head(url).headers
    return(int(headers['content-length']))


def scene_interpreter(scene):
    return({
        'path': scene[3:6],
        'row': scene[6:9],
        'sat': 'L' + scene[2:3],
        'scene': scene
    })


def random_date():
    delta = time.time() - time.mktime(time.strptime('2013-02-11', '%Y-%m-%d'))
    new_time = datetime.utcfromtimestamp(time.time() - delta * random.random())
    return(new_time.strftime('%Y-%m-%d'))
