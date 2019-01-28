import os
import re
import time
import h5py
import random
import shutil
import requests
import MySQLdb as sql
from datetime import datetime


# =================== Path Tools =================== #

def generateFilePathStr(data_dir, sceneid = '', kind = '', file = ''):
	# without other arguments, returns hdf5 file of the main image catalog
	# with arguments, gives the path in the hdf5 file for the given scene and band
	if kind == 'database':
		if sceneid == '': return(os.path.join(data_dir, 'preproc/database.hdf5f'))
		else: return os.path.join(sceneid, file)

	if kind == 'raw':
		if file == 'metadata': file = sceneid + '_MTL.txt'
		elif file == 'tar': file = sceneid
		elif file == 'B1': file = sceneid + '_B1.TIF'
		elif file == 'B2': file = sceneid + '_B2.TIF'
		elif file == 'B3': file = sceneid + '_B3.TIF'
		elif file == 'B4': file = sceneid + '_B4.TIF'
		elif file == 'B5': file = sceneid + '_B5.TIF'
		elif file == 'B6': file = sceneid + '_B6.TIF'
		elif file == 'B7': file = sceneid + '_B7.TIF'
		elif file == 'B8': file = sceneid + '_B8.TIF'
		elif file == 'B9': file = sceneid + '_B9.TIF'
		elif file == 'B10': file = sceneid + '_B10.TIF'
		elif file == 'B11': file = sceneid + '_B11.TIF'
		elif file == 'BQA': file = sceneid + '_BQA.TIF'
		return os.path.join(data_dir, 'raw/{0}/'.format(sceneid), file)

	if kind == 'preproc':
		if file == 'visible' and sceneid != '': sceneid += '_V.TIF'
		if file == 'cloud_detection_clustering': sceneid += '.jpg'
		return os.path.join(data_dir, kind, file, sceneid)

	return data_dir


def check_create_folder(folder_path):
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)
	return folder_path


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
