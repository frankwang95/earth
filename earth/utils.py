import settings
import time
import os



############################### EXCEPTION OBJECT #############################
class ExceptionObj:
	def __init__(self, errCode, traceback = None):
		self.errCode = errCode
		self.traceback = traceback



############################### FILE PATH TOOLS #############################
def generateFilePathStr(sceneid = '', kind = '', file = ''):
	# without other arguments, returns hdf5 file of the main image catalog
	# with arguments, gives the path in the hdf5 file for the given scene and band
	if kind == 'database':
		if sceneid == '': return(os.path.join(settings.DATA_DIR, 'preproc/database.hdf5f'))
		else: return(os.path.join(sceneid, file))

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
		return os.path.join(settings.DATA_DIR, 'raw/{0}/'.format(sceneid), file)

	if kind == 'preproc':
		if file == 'visible': sceneid += '_V.TIF'
		return os.path.join(settings.DATA_DIR, kind, file, sceneid)
		
	return(settings.DATA_DIR)


def check_create_folder(folder_path):
	if not os.path.exists(folder_path):
		os.makedirs(folder_path)
	return folder_path
