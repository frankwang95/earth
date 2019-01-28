FROM baseimage

ENV SERVICE_NAME collection_landsat

ENV BASE_PATH $SVC_PATH/$SERVICE_NAME/
RUN mkdir $BASE_PATH
RUN mkdir $BASE_PATH/logs
WORKDIR $BASE_PATH

# ============= Dependencies ============= #
RUN apt-get update --fix-missing
RUN apt-get install --assume-yes libmariadbclient-dev
RUN apt-get install --assume-yes gcc

ADD . $BASE_PATH
WORKDIR $BASE_PATH
RUN pip install -r requirements.txt

# ============= Source Code ============= #
ADD . $BASE_PATH
RUN pip install .
ENTRYPOINT $BASE_PATH/entrypoint.sh
