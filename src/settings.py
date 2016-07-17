import os



############################### DATA IMPORT SETTINGS #############################
# Storage Location
DATA_DIR = '/Volumes/d1/earth-data/data'


# Search Parameters
CLOUD_MAX = 50
DAY_DELAY = 30


# Download Parameters
DOWNLOAD_TIMEOUT = 10
SATELLITE = 'L8'
L8_METADATA_URL = 'http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_8.csv'
GOOGLE_STORAGE = 'http://storage.googleapis.com/earthengine-public/landsat/'
S3_LANDSAT = 'http://landsat-pds.s3.amazonaws.com/'
API_URL = 'https://api.developmentseed.org/landsat'


# Mysql Parameters
DB_HOST = 'localhost'
DB_USER = 'frankwang'
DB_PASS = 'summertime'