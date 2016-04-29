import os
import tarfile
import io
import re
import requests



############################### EXCEPTION OBJECT #############################
class ExceptionObj:
    def __init__(self, errCode): self.errCode = errCode



############################### TAR STATUS #############################
def get_file_progress_file_object_class():
    class FileProgressFileObject(tarfile.ExFileObject):
        def read(self, size, *args):
          return tarfile.ExFileObject.read(self, size, *args)
    return FileProgressFileObject



class ProgressFileObject(io.FileIO):
    def __init__(self, path, status, *args, **kwargs):
        self._total_size = os.path.getsize(path)
        self.status = status
        self.status.updateTot(self._total_size)
        io.FileIO.__init__(self, path, *args, **kwargs)


    def read(self, size):
        self.status.updateProg(self.tell())
        return io.FileIO.read(self, size)



def extractTar(path, target, status):
    tarfile.TarFile.fileobject = get_file_progress_file_object_class()
    tar = tarfile.open(fileobj=ProgressFileObject(path, status))
    tar.extractall(target)
    tar.close()



############################### MISC #############################
# check whether a folder exists, if not the folder is created.
def check_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path


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
        return(ExceptionObj('File at {0} does not exist'.format(url)))
    return(0)


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


def metadataParser(scene):
    return(0)

