This services opens an API to control the acquisition of landsat imagery. Outside services which need imagery can make use of this API to have the new scene ingested into our data store. The service is designed to ensure consistency and non-duplicity of the store irregardless of the requests it receives though if the service is shutdown in the middle of processing.

# Installing and Running the Service

```
docker build . -t collection_landsat
```
```
export DATA_DIR=/home/fwang/earth_data/
docker run -it --network=host -v $DATA_DIR:/opt/svc/collection_landsat/collection_landsat/resources/data collection_landsat
```

# API

### Usage Notes
