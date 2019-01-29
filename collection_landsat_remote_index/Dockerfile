FROM baseimage

ENV SERVICE_NAME collection_landsat_remote_index

ENV BASE_PATH $SVC_PATH/$SERVICE_NAME/
RUN mkdir $BASE_PATH
RUN mkdir $BASE_PATH/logs
WORKDIR $BASE_PATH

# ============= Dependencies ============= #
# install container wide dependencies
RUN apt-get update --fix-missing
RUN apt-get install --assume-yes gcc libmariadbclient-dev git

# install lib_learning library
RUN git clone https://github.com/frankwang95/lib_learning.git $LIB_PATH/lib_learning
RUN pip install -r $LIB_PATH/lib_learning/requirements_pipelines.txt
RUN pip install $LIB_PATH/lib_learning

# install pypi dependencies
ADD . $BASE_PATH
WORKDIR $BASE_PATH
RUN pip install -r requirements.txt

# ============= Source Code ============= #
ADD . $BASE_PATH
RUN pip install .
ENTRYPOINT $BASE_PATH/entrypoint.sh
