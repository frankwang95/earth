import os



############################### DATA IMPORT SETTINGS #############################
# Storage Location
DATA_DIR = '../data/'
# DATA_DIR = '/opt/earth/data/'


# Search Parameters
CLOUD_MAX = 50
DAY_DELAY = 30


# Download Parameters
DOWNLOAD_TIMEOUT = 2
SATELLITE = 'L8'
L8_METADATA_URL = 'http://landsat.usgs.gov/metadata_service/bulk_metadata_files/LANDSAT_8.csv'
GOOGLE_STORAGE = 'http://storage.googleapis.com/earthengine-public/landsat/'
S3_LANDSAT = 'http://landsat-pds.s3.amazonaws.com/'
API_URL = 'https://api.developmentseed.org/satellites/landsat'


# Mysql Parameters
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASS = ''
DB = 'earthdat'


## In your chosen database, please have the following tables created:
# imageindex(
# 	lid CHAR(21) NOT NULL PRIMARY KEY,
# 	time DATETIME,
# 	ul_lat DECIMAL(15,10),
# 	ul_lon DECIMAL(15,10),
# 	ur_lat DECIMAL(15,10),
# 	ur_lon DECIMAL(15,10),
# 	ll_lat DECIMAL(15,10),
# 	ll_lon DECIMAL(15,10),
# 	lr_lat DECIMAL(15,10),
# 	lr_lon DECIMAL(15,10),
# 	ul_proj_x DECIMAL(15,7),
# 	ul_proj_y DECIMAL(15,7),
# 	ur_proj_x DECIMAL(15,7),
# 	ur_proj_y DECIMAL(15,7),
# 	ll_proj_x DECIMAL(15,7),
# 	ll_proj_y DECIMAL(15,7),
# 	lr_proj_x DECIMAL(15,7),
# 	lr_proj_y DECIMAL(15,7),
# 	cloud_cover DECIMAL(4,2),
# 	roll_angle DECIMAL(5,4),
# 	sun_azimuth DECIMAL(15,10),
# 	sun_elev DECIMAL(15,10),
# 	earth_sun_dist DECIMAL(15,10),
# 	orientation VARCHAR(20)
# )