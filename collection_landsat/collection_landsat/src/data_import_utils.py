import os
import re
import time
import h5py
import random
import shutil
import requests
import MySQLdb as sql
from datetime import datetime


# =================== SQL =================== #

def check_scene_exists(sceneid, db, cur):
    enterCmd = 'SELECT lid FROM imageindex WHERE lid="{0}";'.format(sceneid)
    code = cur.execute(enterCmd)
    return code != 0


def remove_scene(sceneid, db, cur):
    enterCmd = 'DELETE FROM imageindex WHERE lid="{0}";'.format(sceneid)
    cur.execute(enterCmd)
    db.commit()


# =================== Cleanup =================== #

def purge_scene(sceneid, data_dir, db, cur, h5F):
    try:
        for i in os.listdir(generateFilePathStr(data_dir, sceneid, 'raw')):
            os.remove(generateFilePathStr(data_dir, sceneid, 'raw', i))
    except: pass

    try: os.rmdir(generateFilePathStr(data_dir, sceneid, 'raw'))
    except: pass

    try: os.remove(generateFilePathStr(data_dir, sceneid, 'preproc', 'visible'))
    except: pass

    try: remove_scene(sceneid, db, cur)
    except: pass

    try: del h5F[sceneid]
    except: pass


def cleanup(data_dir, db, cur, h5F):
    # get image lists
    sqlcmd = 'SELECT lid FROM imageindex;'
    cur.execute(sqlcmd)
    sql_lid = cur.fetchall()
    sql_lid = [i[0] for i in sql_lid]
    raw_lid = [i for i in os.listdir(generateFilePathStr(data_dir, kind='raw')) if i[0] != '.']
    vis_lid = [i[:-6] for i in os.listdir(generateFilePathStr(data_dir, kind='preproc', file='visible')) if i[0] != '.']
    hdf_lid = h5F.keys()
    lids = list(set().union(sql_lid, raw_lid, vis_lid, hdf_lid))

    for l in lids:
        if l not in vis_lid or l not in hdf_lid or l not in raw_lid or l not in sql_lid: purge_scene(l, data_dir, db, cur, h5F)


# =================== MISC =================== #

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
        return number


def remote_file_exists(url):
    status = requests.head(url).status_code
    if status != 200:
        return False
    return True


def get_remote_file_size(url):
    headers = requests.head(url).headers
    return int(headers['content-length'])


def scene_interpreter(scene):
    return {
        'path': scene[3:6],
        'row': scene[6:9],
        'sat': 'L' + scene[2:3],
        'scene': scene
    }


def random_date():
    delta = time.time() - time.mktime(time.strptime('2013-02-11', '%Y-%m-%d'))
    new_time = datetime.utcfromtimestamp(time.time() - delta * random.random())
    return new_time.strftime('%Y-%m-%d')
