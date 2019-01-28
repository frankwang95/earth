from setuptools import setup, find_packages, Extension
from Cython.Build import cythonize
import numpy as np


exts = cythonize([Extension(
	"pyPreProcPipe",
	sources=[
		"collection_landsat/src/cython/cPreProcPipe.c",
		"collection_landsat/src/cython/pyPreProcPipe.pyx"
	],
	include_dirs=[np.get_include()]
)])


setup(
	name='collection_landsat',
	version='0.0.0',
	author='Frank Wang',
	author_email='fkwang95@gmail.com',
	packages=find_packages(),
	ext_modules=exts,
	include_package_data=True
)
