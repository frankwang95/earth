from os.path import join, exists, getsize
import os
import requests

from utils import(
    check_create_folder,
    url_builder,
    remote_file_exists,
    get_remote_file_size,
    scene_interpreter,
    extractTar,
    metadataParser,
    ExceptionObj
)
import settings



class DownloadStatus:
    def __init__(self, total):
        self.prog = 0
        self.tot = total

    def update(self, change):
        self.prog += change
        print('Download: {0}/{1}'.format(self.prog, self.tot))
        return(0)
        


class ExtractionStatus:
    def __init__(self):
        self.prog = 0
        self.tot = 1
    
    def updateTot(self, total):
        self.tot = total
        return(0)

    def updateProg(self, change):
        print('Extract: {0}/{1}'.format(self.prog, self.tot))
        self.prog = change
        return(0)



class Downloader(object):
    def __init__(self, verbose=False, download_dir=settings.DOWNLOAD_DIR):
        self.status = None
        self.download_dir = download_dir
        self.google = settings.GOOGLE_STORAGE
        self.s3 = settings.S3_LANDSAT
        check_create_folder(self.download_dir)


    def download(self, scene):
        if str(scene) in os.listdir(self.download_dir):
            return(ExceptionObj('Scene {0} already exists'.format(scene)))
        check_create_folder(self.download_dir + '/' + scene)

        return(self.google_storage(scene))
        #if code != 0: self.amazon_s3(scene)


    def google_storage(self, scene):
        interpScene = scene_interpreter(scene)
        url = self.google_storage_url(interpScene)
        check = remote_file_exists(url)

        if check == 0:
            self.fetch(url, scene)
            return(0)
        return(check)


    def amazon_s3(self, scene, bands):
        interpScene = scene_interpreter(scene)
        url = None
        check = remote_file_exists(url)
        return(check)


    def fetch(self, url, scene):
        total = get_remote_file_size(url)
        self.status = DownloadStatus(total)

        r = requests.get(url, stream = True)
        f = open(self.download_dir + '/' + scene + 'temp', 'wb')
        for chunk in r.iter_content(chunk_size=2048): 
            if chunk:
                f.write(chunk)
                self.status.update(len(chunk))
        f.close()

        self.status = ExtractionStatus()
        extractTar(
            self.download_dir + '/' + scene + 'temp',
            self.download_dir + '/' + scene,
            self.status
        )
        os.remove(self.download_dir + '/' + scene + 'temp')
        self.status = None
        return(0)


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

d = Downloader()
d.download('LC81420402016114LGN00')
print('done')
