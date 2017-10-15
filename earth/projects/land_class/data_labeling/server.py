from flask import Flask
from earth.projects.land_class.data_labeling.loader import DataLabelLoader


loader = DataLabelLoader()
app = Flask('land-classification_labeling-service')
