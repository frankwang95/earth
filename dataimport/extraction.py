from os.path import join, exists, getsize
import os
import tarfile

from utils import ExceptionObj, ExtractionStatus
import settings




############################### TAR EXTRACTION #############################
def extractTar(path, target, status):
    tar = tarfile.open(path)
    members = tar.getmembers()
    status.updateTot(len(members))
    for m in members:
        tar.extract(m, target)
        status.updateProg()
    tar.close()



############################### METADATA PARSER #############################
def metadataParser():
    return(0)



############################### EXTRACTORC CLASS #############################
class Extractor(object):
    def __init__(self, download_dir=settings.DOWNLOAD_DIR):
        self.status = 'IDLE'
        self.download_dir = download_dir


    def extract(self, scene, status=None):
        if not os.path.exists(self.download_dir + '/' + scene + '/' + scene):
            return(ExceptionObj('Requested scene {0} has not yet been downloaded'.format(scene)))

        if status==None: self.status = ExtractionStatus()
        else: self.status = status

        extractTar(
            self.download_dir + '/' + scene + '/' + scene,
            self.download_dir + '/' + scene,
            self.status
        )
        os.remove(self.download_dir + '/' + scene + '/' + scene)