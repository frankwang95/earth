from os.path import join, exists, getsize
import os
import requests

from utils import(
    check_create_folder,
    url_builder,
    remote_file_exists,
    get_remote_file_size,
    scene_interpreter,
    ExceptionObj,
    DownloadStatus
)
import settings




class Downloader(object):
    def __init__(self, download_dir=settings.DOWNLOAD_DIR):
        self.status = 'IDLE'
        self.download_dir = download_dir
        self.google = settings.GOOGLE_STORAGE
        self.s3 = settings.S3_LANDSAT
        check_create_folder(self.download_dir)


    def download(self, scene, status=None):
        if str(scene) in os.listdir(self.download_dir):
            return(ExceptionObj('Scene {0} already exists'.format(scene)))
        check_create_folder(self.download_dir + '/' + scene)

        return(self.google_storage(scene, status))
        #if code != 0: self.amazon_s3(scene)


    def google_storage(self, scene, status):
        interpScene = scene_interpreter(scene)
        url = self.google_storage_url(interpScene)
        check = remote_file_exists(url)

        if check == 0: return(self.fetch(url, scene, status))
        return(check)


    def amazon_s3(self, scene, bands):
        interpScene = scene_interpreter(scene)
        url = None
        check = remote_file_exists(url)
        return(check)


### Gets google download url given an interpreted scene ID
    def google_storage_url(self, sat):
        filename = sat['scene'] + '.tar.bz'
        return url_builder([self.google, sat['sat'], sat['path'], sat['row'], filename])


### Gets amazon url given an interpreted scene ID
    def amazon_s3_url(self, sat):
        if band != 'MTL':
            filename = '%s_B%s.TIF' % (sat['scene'], band)
        else:
            filename = '%s_%s.txt' % (sat['scene'], band)
        return url_builder([self.s3, sat['sat'], sat['path'], sat['row'], sat['scene'], filename])


    def fetch(self, url, scene, status):
        print status
        if status==None:
            self.status = DownloadStatus()
        else: self.status = status

        self.status.updateTotal(get_remote_file_size(url))



        r = requests.get(url, stream = True)
        f = open(self.download_dir + '/' + scene + '/' + scene, 'wb')
        for chunk in r.iter_content(chunk_size=2048): 
            if chunk:
                f.write(chunk)
                self.status.updateProg(len(chunk))
        f.close()

        self.status.completed()
        self.status = 'IDLE'
        return(0)