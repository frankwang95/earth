# Image Index Database

Entries in this database are populated from the included Landsat 8 metadata. Specific details about any of the fields found here can be obtained by reference to the LandSat documentation.

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
	cloud_cover DECIMAL(15,10),
	roll_angle DECIMAL(15,10),
	sun_azimuth DECIMAL(15,10),
	sun_elev DECIMAL(15,10),
	earth_sun_dist DECIMAL(15,10),
	orientation VARCHAR(20),
	ls_row SMALLINT UNSIGNED,
	ls_path SMALLINT UNSIGNED
)
'''


# Remote Image Index Database

'''
remote_imageindex(
	lid CHAR(50) NOT NULL PRIMARY KEY,
	aquisition_date DATETIME,
	ingestion_date DATETIME,
	category VARCHAR(3),
	correction_level VARCHAR(5),
	ls_row SMALLINT UNSIGNED,
	ls_path SMALLINT UNSIGNED,
	cloud_cover DECIMAL(15,10),
	sun_azimuth DECIMAL(15,10),
	sun_elev DECIMAL(15,10),
	ul_lat DECIMAL(15,10),
	ul_lon DECIMAL(15,10),
	ur_lat DECIMAL(15,10),
	ur_lon DECIMAL(15,10),
	ll_lat DECIMAL(15,10),
	ll_lon DECIMAL(15,10),
	lr_lat DECIMAL(15,10),
	lr_lon DECIMAL(15,10)
)
'''
