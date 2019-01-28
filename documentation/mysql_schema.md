# --------- Image Index Database
# --------- Entries are consistent with Landsat 8 metadata - see their documentation
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
	orientation VARCHAR(20),
	row SMALLINT UNSIGNED,
	path SMALLINT UNSIGNED
)
'''


# --------- Table recording status for each labeled entry for the cloud-segmentation project
'''
cloud_detection_clustering(
	lid CHAR(21) NOT NULL PRIMARY KEY,
	result SMALLINT UNSIGNED NOT NULL
)
'''

# result coding:
# -- 0 success
# -- 1 failed
# -- 2 snow


# --------- Labeled open Danish AIS data
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
