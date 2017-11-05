############################### DATA IMPORT SETTINGS #############################
# Storage Location
DATA_DIR = '/opt/earth_data/'
# DATA_DIR = '/Users/frankwang/projects/earth/data'

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


############################### MYSQL DATABASES #############################
#### Image Index Database
# Entries are consistent with Landsat 8 metadata - see their documentation
'''
imageindex(
	lid CHAR(21) NOT NULL PRIMARY KEY,
	time DATETIME,
	ul_lat DECIMAL(15,10),
	ul_lon DECIMAL(15,10),
	ur_lat DECIMAL(15,10),
	ur_lon DECIMAL(15,10),
	ll_lat DECIMAL(15,10),
	ll_lon DECIMAL(15,10),
	lr_lat DECIMAL(15,10),
	lr_lon DECIMAL(15,10),
	ul_proj_x DECIMAL(15,7),
	ul_proj_y DECIMAL(15,7),
	ur_proj_x DECIMAL(15,7),
	ur_proj_y DECIMAL(15,7),
	ll_proj_x DECIMAL(15,7),
	ll_proj_y DECIMAL(15,7),
	lr_proj_x DECIMAL(15,7),
	lr_proj_y DECIMAL(15,7),
	cloud_cover DECIMAL(4,2),
	roll_angle DECIMAL(5,4),
	sun_azimuth DECIMAL(15,10),
	sun_elev DECIMAL(15,10),
	earth_sun_dist DECIMAL(15,10),
	orientation VARCHAR(20)
)
'''

#### Cloud Detection Clustering Data with K-Means @ 2 using a 32x32 grid
# labels coding:
## 0 cloud
## 1 not cloud
## 2 unknown
'''
cloud_detection_kmeans2(
	entry_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	lid CHAR(21) NOT NULL,
	x_coord SMALLINT UNSIGNED NOT NULL,
	y_coord SMALLINT UNSIGNED NOT NULL,
	label TINYINT UNSIGNED
)
'''

#### Labeled open Danish AIS data
'''
denmark_ais(
	entry_id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
	timestamp DATETIME,
	vessel_type TEXT,
	mmsi INT UNSIGNED,
	latitude DOUBLE,
	longitude DOUBLE,
	navigational_status TEXT,
	rate_of_turn FLOAT,
	speed_over_ground FLOAT,
	course_over_ground FLOAT,
	heading SMALLINT UNSIGNED,
	imo INT UNSIGNED,
	callsign VARCHAR(16),
	name TEXT,
	ship_type TEXT,
	width SMALLINT UNSIGNED,
	length SMALLINT UNSIGNED,
	position_fixing_method TEXT,
	draught FLOAT UNSIGNED,
	data_source TEXT
)
'''
